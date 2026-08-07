from ubuntu_ai.autonomy.goal import Goal
from ubuntu_ai.autonomy.goal_manager import GoalManager
from ubuntu_ai.autonomy.models import AutonomousCycleResult
from ubuntu_ai.autonomy.runtime import AutonomousRuntime


class FakeController:
    def run_once(
        self,
        goal_id,
        *,
        session_id,
        execute=True,
        execution_action=None,
    ):
        return AutonomousCycleResult(
            goal=Goal(
                goal_id=goal_id,
                description="status",
            ),
            runtime_result=None,
            completed=True,
            retry_scheduled=False,
            reason="ok",
        )


def test_autonomous_runtime_registers_and_runs_goal() -> None:
    manager = GoalManager()
    runtime = AutonomousRuntime(
        controller=FakeController(),
        goal_manager=manager,
    )

    runtime.register_goal(
        Goal(
            goal_id="g1",
            description="status",
        )
    )

    result = runtime.run_once(
        "g1",
        session_id="s",
    )

    assert result.completed
