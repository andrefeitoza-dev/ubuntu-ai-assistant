from ubuntu_ai.container.container import Container


def test_container_builds_singleton_capability_registry() -> None:
    container = Container()

    assert container.capability_registry() is container.capability_registry()
    assert container.capability_registry().get("apt").name == "apt"


def test_container_wires_tool_selection_into_planner() -> None:
    container = Container()

    plan = container.planner().create_plan("Instale Docker")

    assert [step.tool_name for step in plan.steps] == [
        "apt",
        "apt",
        "systemctl",
        "docker",
    ]
