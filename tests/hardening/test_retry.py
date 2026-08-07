from ubuntu_ai.hardening.retry import RetryPolicy


def test_retry_policy_allows_transient_idempotent_failure() -> None:
    decision = RetryPolicy().evaluate(
        error=TimeoutError("timeout"),
        attempt=1,
        idempotent=True,
    )

    assert decision.retry
    assert decision.delay_seconds > 0


def test_retry_policy_blocks_non_idempotent_retry() -> None:
    decision = RetryPolicy().evaluate(
        error=TimeoutError("timeout"),
        attempt=1,
        idempotent=False,
    )

    assert not decision.retry
