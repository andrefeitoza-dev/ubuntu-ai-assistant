from ubuntu_ai.memory.models import ExecutionRecord
from ubuntu_ai.memory_intelligence.execution_memory import ExecutionMemoryBuilder
from ubuntu_ai.memory_intelligence.models import MemoryKind


def test_execution_record_becomes_memory_candidate() -> None:
    record = ExecutionRecord.create(
        session_id="test-session",
        user_request="verifique o disco",
        command="df -h",
        status="executed",
        message="Executado com sucesso.",
        working_directory="/tmp/ubuntu-ai-assistant",
        project_name="ubuntu-ai-assistant",
        return_code=0,
    )

    memory = ExecutionMemoryBuilder().build(record)

    assert memory.kind is MemoryKind.EXECUTION
    assert memory.project_name == "ubuntu-ai-assistant"
    assert memory.source == "execution_history"
    assert memory.success_signal == 1.0
    assert "verifique o disco" in memory.content
    assert "df -h" in memory.content
    assert "executed" in memory.content
