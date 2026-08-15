from ubuntu_ai.execution_intelligence.discovery import DiscoveryEngine


def test_discovers_python_executable() -> None:
    result = DiscoveryEngine().discover_executable("python")
    assert result.available is True
    assert result.path is not None


def test_caches_discovery_result() -> None:
    engine = DiscoveryEngine()
    first = engine.discover_executable("python")
    second = engine.discover_executable("python")
    assert first is second
