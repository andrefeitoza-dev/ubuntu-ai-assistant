from ubuntu_ai.application.runtime import ApplicationRuntime
from ubuntu_ai.autonomy.runtime import AutonomousRuntime
from ubuntu_ai.container import Container
from ubuntu_ai.remote.engine import RemoteExecutionEngine
from ubuntu_ai.runtime_integration.runtime import MultiAgentRuntime


def test_container_composes_application_runtime_as_singleton() -> None:
    container = Container()

    first = container.application_runtime()
    second = container.application_runtime()

    assert isinstance(first, ApplicationRuntime)
    assert first is second
    assert isinstance(first.multi_agent, MultiAgentRuntime)
    assert isinstance(first.autonomous, AutonomousRuntime)
    assert isinstance(first.remote, RemoteExecutionEngine)
