from ubuntu_ai.reflection.failure import FailureKind
from ubuntu_ai.reflection.v2 import ReflectionEngineV2


def test_engine_builds_complete_report() -> None:
    report = ReflectionEngineV2().reflect(
        success=False,
        stderr="Connection refused",
    )

    assert report.failure.kind is FailureKind.NETWORK
    assert report.root_cause.title
    assert report.recovery.retry_allowed
    assert report.critique.findings
    assert report.retry_allowed


def test_unknown_failure_requires_review() -> None:
    report = ReflectionEngineV2().reflect(
        success=False,
        stderr="mysterious kernel issue",
    )

    assert report.failure.kind is FailureKind.UNKNOWN
    assert not report.retry_allowed
    assert report.recovery.requires_confirmation
