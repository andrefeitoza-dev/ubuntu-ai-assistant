from ubuntu_ai.agent_loop import AgentLoopController
from ubuntu_ai.container.container import Container


def test_container_exposes_agent_loop_controller() -> None:
    container = Container()

    assert isinstance(container.agent_loop_controller(), AgentLoopController)
    assert container.agent_loop_controller() is container.agent_loop_controller()
