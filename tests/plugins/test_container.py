from ubuntu_ai.container.container import Container


def test_container_exposes_plugin_sdk_singletons() -> None:
    container = Container()

    assert container.plugin_registry() is container.plugin_registry()
    assert container.plugin_manager() is container.plugin_manager()
    assert container.plugin_policy() is container.plugin_policy()
