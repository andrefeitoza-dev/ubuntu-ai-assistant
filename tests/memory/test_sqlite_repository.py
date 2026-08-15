from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from ubuntu_ai.memory.models import ExecutionRecord
from ubuntu_ai.memory.sqlite_repository import SQLiteMemoryRepository


def create_record(
    *,
    record_id: str,
    created_at: datetime,
    status: str = "executed",
    project_name: str | None = "ubuntu-ai",
) -> ExecutionRecord:
    return ExecutionRecord(
        id=record_id,
        created_at=created_at,
        session_id="session-1",
        user_request="Execute um comando",
        command=f"echo {record_id}",
        status=status,
        message="Resultado",
        working_directory="/tmp",
        project_name=project_name,
        return_code=0,
        stdout="ok",
        duration=0.1,
    )


def test_repository_creates_database_and_round_trips_record(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "nested" / "memory.db"
    repository = SQLiteMemoryRepository(database_path)
    record = create_record(
        record_id="record-1",
        created_at=datetime.now(UTC),
    )

    repository.save_execution(record)

    assert database_path.exists()
    assert repository.get_execution(record.id) == record


def test_repository_returns_last_execution_and_filtered_lists(
    tmp_path: Path,
) -> None:
    repository = SQLiteMemoryRepository(tmp_path / "memory.db")
    now = datetime.now(UTC)

    older = create_record(
        record_id="older",
        created_at=now - timedelta(hours=2),
        status="failed",
    )
    newer = create_record(
        record_id="newer",
        created_at=now,
        status="executed",
    )

    repository.save_execution(older)
    repository.save_execution(newer)

    assert repository.get_last_execution() == newer
    assert repository.list_executions(status="failed") == (older,)
    assert repository.list_executions(project_name="ubuntu-ai") == (
        newer,
        older,
    )
    assert repository.count_executions(status="failed") == 1


def test_repository_applies_since_filter(tmp_path: Path) -> None:
    repository = SQLiteMemoryRepository(tmp_path / "memory.db")
    now = datetime.now(UTC)
    repository.save_execution(
        create_record(
            record_id="old",
            created_at=now - timedelta(days=2),
        )
    )
    recent = create_record(
        record_id="recent",
        created_at=now - timedelta(hours=1),
    )
    repository.save_execution(recent)

    assert repository.list_executions(since=now - timedelta(days=1)) == (recent,)


def test_repository_rejects_invalid_limit(tmp_path: Path) -> None:
    repository = SQLiteMemoryRepository(tmp_path / "memory.db")

    with pytest.raises(ValueError, match="limite"):
        repository.list_executions(limit=0)
