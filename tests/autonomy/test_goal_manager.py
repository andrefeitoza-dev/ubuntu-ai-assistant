from ubuntu_ai.autonomy.goal import Goal
from ubuntu_ai.autonomy.goal_manager import GoalManager


def test_goal_manager_registers_goal() -> None:
    manager = GoalManager()
    goal = Goal(goal_id="g1", description="status")

    manager.add(goal)

    assert manager.get("g1") == goal
    assert len(manager.active()) == 1
