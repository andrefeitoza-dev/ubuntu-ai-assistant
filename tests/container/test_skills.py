from ubuntu_ai.container.container import Container


def test_container_composes_capabilities_from_skills() -> None:
    container = Container()

    assert container.skill_registry().for_capability("git").name == "version-control"
    assert container.capability_registry().get("git").name == "git"
    assert container.skill_manager() is container.skill_manager()
