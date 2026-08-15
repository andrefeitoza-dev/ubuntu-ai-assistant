from ubuntu_ai.reflection.failure import FailureAnalysis, FailureKind
from ubuntu_ai.reflection.recovery import RecoveryAction, RecoveryPlanner


def test_network_failure_can_retry() -> None:
    plan = RecoveryPlanner().build(
        FailureAnalysis(
            kind=FailureKind.NETWORK,
            confidence=0.8,
            summary="network",
        )
    )

    assert plan.retry_allowed
    assert RecoveryAction.VERIFY_NETWORK in plan.actions
    assert RecoveryAction.RETRY in plan.actions


def test_permission_failure_requires_confirmation() -> None:
    plan = RecoveryPlanner().build(
        FailureAnalysis(
            kind=FailureKind.PERMISSION,
            confidence=0.8,
            summary="permission",
        )
    )

    assert not plan.retry_allowed
    assert plan.requires_confirmation
