from dataclasses import dataclass

from ubuntu_ai.autonomy.goal import Goal, GoalStatus
from ubuntu_ai.autonomy.goal_manager import GoalManager
from ubuntu_ai.autonomy.loop_controller import AutonomousLoopController
from ubuntu_ai.runtime_integration.models import (
    RuntimeCycleResult,
    RuntimeStage,
)
from ubuntu_ai.reflection.v2 import ReflectionEngineV2


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
