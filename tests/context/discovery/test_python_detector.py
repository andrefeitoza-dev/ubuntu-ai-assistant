from ubuntu_ai.context.discovery.python_detector import PythonDetector


def test_detect_python_version() -> None:
    detector = PythonDetector()

    version = detector.version()

    assert isinstance(version, str)
    assert version


def test_virtual_environment() -> None:
    detector = PythonDetector()

    value = detector.virtual_environment()

    assert value is None or isinstance(value, str)