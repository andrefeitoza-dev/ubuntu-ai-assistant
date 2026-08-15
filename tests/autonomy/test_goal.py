import pytest

from ubuntu_ai.autonomy.goal import Goal, GoalStatus


def test_goal_updates_status_and_attempts() -> None:
    goal = Goal(
        goal_id="g1",
        description="status do sistema",
    )

    updated = goal.with_status(GoalStatus.RUNNING).increment_attempts()

    assert updated.status is GoalStatus.RUNNING
    assert updated.attempts == 1


def test_goal_rejects_empty_description() -> None:
    with pytest.raises(ValueError):
        Goal(goal_id="g", description="")
