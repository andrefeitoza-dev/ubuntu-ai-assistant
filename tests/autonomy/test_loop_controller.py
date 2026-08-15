from ubuntu_ai.autonomy.goal import Goal, GoalStatus
from ubuntu_ai.autonomy.goal_manager import GoalManager
from ubuntu_ai.autonomy.loop_controller import AutonomousLoopController
from ubuntu_ai.reflection.v2 import ReflectionEngineV2
from ubuntu_ai.runtime_integration.models import (
    RuntimeCycleResult,
    RuntimeStage,
)


class FakeRuntime:
    def __init__(self, result):
        self.result = result

    def run(self, request, execution_action=None):
        return self.result


def test_loop_marks_successful_goal_completed() -> None:
    manager = GoalManager()
    manager.add(
        Goal(
            goal_id="g1",
            description="status",
        )
    )

    reflection = ReflectionEngineV2().reflect(success=True)

    controller = AutonomousLoopController(
        runtime=FakeRuntime(
            RuntimeCycleResult(
                stage=RuntimeStage.COMPLETED,
                reflection=reflection,
            )
        ),
        goal_manager=manager,
    )

    result = controller.run_once(
        "g1",
        session_id="s",
    )

    assert result.completed
    assert result.goal.status is GoalStatus.COMPLETED


class SequentialRuntime:
    def __init__(self, results):
        self.results = list(results)
        self.calls = 0

    def run(self, request, execution_action=None):
        result = self.results[self.calls]
        self.calls += 1
        return result


def test_loop_retries_safe_failure_until_success() -> None:
    manager = GoalManager()
    manager.add(
        Goal(
            goal_id="retry-goal",
            description="verificar serviço",
            max_attempts=3,
        )
    )

    engine = ReflectionEngineV2()

    retryable_failure = engine.reflect(
        success=False,
        stderr="network connection timeout",
    )
    success = engine.reflect(success=True)

    runtime = SequentialRuntime(
        [
            RuntimeCycleResult(
                stage=RuntimeStage.COMPLETED,
                reflection=retryable_failure,
            ),
            RuntimeCycleResult(
                stage=RuntimeStage.COMPLETED,
                reflection=success,
            ),
        ]
    )

    controller = AutonomousLoopController(
        runtime=runtime,
        goal_manager=manager,
    )

    result = controller.run_until_done(
        "retry-goal",
        session_id="s",
    )

    assert result.completed
    assert result.goal.status is GoalStatus.COMPLETED
    assert result.goal.attempts == 2
    assert runtime.calls == 2


def test_loop_stops_when_recovery_is_not_safe() -> None:
    manager = GoalManager()
    manager.add(
        Goal(
            goal_id="unsafe-goal",
            description="acessar recurso inexistente",
            max_attempts=3,
        )
    )

    reflection = ReflectionEngineV2().reflect(
        success=False,
        stderr="file not found",
    )

    runtime = SequentialRuntime(
        [
            RuntimeCycleResult(
                stage=RuntimeStage.COMPLETED,
                reflection=reflection,
            ),
        ]
    )

    controller = AutonomousLoopController(
        runtime=runtime,
        goal_manager=manager,
    )

    result = controller.run_until_done(
        "unsafe-goal",
        session_id="s",
    )

    assert not result.completed
    assert not result.retry_scheduled
    assert result.goal.attempts == 1
    assert runtime.calls == 1


def test_loop_respects_max_attempts() -> None:
    manager = GoalManager()
    manager.add(
        Goal(
            goal_id="max-attempts-goal",
            description="verificar serviço remoto",
            max_attempts=2,
        )
    )

    engine = ReflectionEngineV2()

    retryable_failure = engine.reflect(
        success=False,
        stderr="network connection timeout",
    )

    runtime = SequentialRuntime(
        [
            RuntimeCycleResult(
                stage=RuntimeStage.COMPLETED,
                reflection=retryable_failure,
            ),
            RuntimeCycleResult(
                stage=RuntimeStage.COMPLETED,
                reflection=retryable_failure,
            ),
        ]
    )

    controller = AutonomousLoopController(
        runtime=runtime,
        goal_manager=manager,
    )

    result = controller.run_until_done(
        "max-attempts-goal",
        session_id="s",
    )

    assert not result.completed
    assert not result.retry_scheduled
    assert result.goal.status is GoalStatus.FAILED
    assert result.goal.attempts == 2
    assert runtime.calls == 2
