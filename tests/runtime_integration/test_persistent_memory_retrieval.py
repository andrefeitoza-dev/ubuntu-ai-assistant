from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.agents.memory_agent import MemoryAgent
from ubuntu_ai.agents.registry import AgentRegistry
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.memory.service import MemoryService
from ubuntu_ai.memory.sqlite_repository import SQLiteMemoryRepository
from ubuntu_ai.runtime_integration.memory_bridge import RuntimeMemoryBridge


def test_runtime_memory_bridge_recovers_persisted_execution(tmp_path) -> None:
    repository = SQLiteMemoryRepository(tmp_path / "memory.db")
    memory_service = MemoryService(repository)

    memory_service.record_execution(
        session_id="previous-session",
        user_request="verifique o disco",
        working_directory="/tmp/ubuntu-ai-assistant",
        project_name="ubuntu-ai-assistant",
        result=ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Executado com sucesso.",
            command="df -h",
            return_code=0,
        ),
    )

    registry = AgentRegistry()
    registry.register(MemoryAgent())

    coordinator = AgentCoordinator(registry)

    bridge = RuntimeMemoryBridge(
        coordinator,
        memory_service=memory_service,
    )

    context = ContextSnapshot(
        session_id="new-session",
        working_directory=tmp_path,
        operating_system="Ubuntu",
        project_name="ubuntu-ai-assistant",
    )

    selection = bridge.select(
        request_text="verifique o disco",
        context=context,
        candidates=(),
    )

    assert not selection.is_empty()

    candidate = selection.items[0].candidate

    assert candidate.kind.value == "execution"
    assert candidate.source == "execution_history"
    assert candidate.project_name == "ubuntu-ai-assistant"
    assert "verifique o disco" in candidate.content
    assert "df -h" in candidate.content
