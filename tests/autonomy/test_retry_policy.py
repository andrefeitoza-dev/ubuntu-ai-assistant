from ubuntu_ai.autonomy.goal import Goal
from ubuntu_ai.autonomy.retry_policy import RetryPolicy
from ubuntu_ai.reflection.v2 import ReflectionEngineV2


def test_retry_policy_allows_recoverable_network_failure() -> None:
    goal = Goal(
        goal_id="g",
        description="download",
        attempts=1,
        max_attempts=3,
    )

    reflection = ReflectionEngineV2().reflect(
        success=False,
        stderr="Connection refused",
    )

    decision = RetryPolicy().evaluate(goal, reflection)

    assert decision.retry
