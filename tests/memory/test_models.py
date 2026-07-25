from datetime import UTC

from ubuntu_ai.memory.models import ExecutionRecord, MemoryEventType


def test_execution_record_create_generates_identity_and_utc_timestamp() -> None:
    record = ExecutionRecord.create(
        session_id="session-1",
        user_request="Atualize o sistema",
        command="apt update",
        status="executed",
        message="Comando executado.",
        working_directory="/tmp/project",
        project_name="project",
    )

    assert record.id
    assert record.created_at.tzinfo is UTC
    assert record.event_type is MemoryEventType.EXECUTION
    assert record.command == "apt update"
    assert record.project_name == "project"
