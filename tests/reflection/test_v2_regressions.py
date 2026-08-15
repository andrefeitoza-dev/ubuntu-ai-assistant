from ubuntu_ai.reflection.failure import FailureClassifier, FailureKind


def test_invalid_argument_classification() -> None:
    result = FailureClassifier().classify(
        success=False,
        stderr="invalid argument --foo",
    )
    assert result.kind is FailureKind.INVALID_INPUT


def test_timeout_classification() -> None:
    result = FailureClassifier().classify(
        success=False,
        stderr="operation timed out",
    )
    assert result.kind is FailureKind.TIMEOUT


def test_dependency_classification() -> None:
    result = FailureClassifier().classify(
        success=False,
        stderr="ModuleNotFoundError: no module named x",
    )
    assert result.kind is FailureKind.DEPENDENCY


def test_not_found_classification() -> None:
    result = FailureClassifier().classify(
        success=False,
        stderr="command not found",
    )
    assert result.kind is FailureKind.NOT_FOUND
