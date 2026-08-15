from ubuntu_ai.reflection.critique import SelfCritic
from ubuntu_ai.reflection.failure import FailureAnalysis, FailureKind
from ubuntu_ai.reflection.recovery import RecoveryPlan
from ubuntu_ai.reflection.root_cause import RootCause


def test_successful_execution_is_approved() -> None:
    critique = SelfCritic().evaluate(
        failure=FailureAnalysis(
            kind=FailureKind.NONE,
            confidence=1.0,
            summary="ok",
        ),
        root_cause=RootCause("Sem falha", "ok", 1.0),
        recovery=RecoveryPlan(
            actions=(),
            retry_allowed=False,
            requires_confirmation=False,
        ),
    )

    assert critique.approved
    assert critique.score == 1.0
