from ubuntu_ai.container.container import Container


def test_container_composes_execution_intelligence_as_singleton() -> None:
    container = Container()
    assert container.execution_intelligence() is container.execution_intelligence()
    assert container.preflight_engine() is container.preflight_engine()
    assert container.discovery_engine() is container.discovery_engine()
