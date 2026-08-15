from ubuntu_ai.reflection.failure import FailureClassifier, FailureKind


def test_classifier_recognizes_permission_error() -> None:
    analysis = FailureClassifier().classify(
        success=False,
        stderr="Permission denied",
    )

    assert analysis.kind is FailureKind.PERMISSION
    assert analysis.failed
    assert analysis.confidence >= 0.7


def test_classifier_recognizes_network_error() -> None:
    analysis = FailureClassifier().classify(
        success=False,
        stderr="Network is unreachable",
    )

    assert analysis.kind is FailureKind.NETWORK


def test_success_has_no_failure() -> None:
    analysis = FailureClassifier().classify(success=True)

    assert analysis.kind is FailureKind.NONE
    assert not analysis.failed
