from ubuntu_ai.reflection.failure import FailureAnalysis, FailureKind
from ubuntu_ai.reflection.root_cause import RootCauseAnalyzer


def test_root_cause_for_dependency() -> None:
    cause = RootCauseAnalyzer().analyze(
        FailureAnalysis(
            kind=FailureKind.DEPENDENCY,
            confidence=0.8,
            summary="dependency",
        )
    )

    assert "Dependência" in cause.title
    assert cause.confidence == 0.8
