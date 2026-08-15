from ubuntu_ai.container.container import Container


def test_container_reuses_reflection_engine() -> None:
    container = Container()

    assert container.reflection_engine() is container.reflection_engine()
