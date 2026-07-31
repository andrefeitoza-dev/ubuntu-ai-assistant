from datetime import UTC, datetime
from pathlib import Path

import pytest

from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.memory.service import MemoryService
from ubuntu_ai.memory.sqlite_repository import SQLiteMemoryRepository


def build_service(tmp_path: Path) -> MemoryService:
    repository = SQLiteMemoryRepository(tmp_path / "memory.db")
    return MemoryService(repository)


def test_service_records_complete_execution(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    result = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        message="Executado.",
        command="echo ok",
        return_code=0,
        stdout="ok\n",
        duration=0.25,
    )

    record = service.record_execution(
        session_id="session-1",
        user_request="Mostre ok",
        working_directory="/tmp/project",
        project_name="project",
        result=result,
    )

    assert service.last_execution() == record
    assert record.status == "executed"
    assert record.stdout == "ok\n"
    assert record.duration == 0.25


def test_service_rejects_result_without_command(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    result = ExecutionResult(
        status=ExecutionStatus.FAILED,
        message="Falhou.",
    )

    with pytest.raises(ValueError, match="comando"):
        service.record_execution(
            session_id="session-1",
            user_request="Execute",
            working_directory="/tmp",
            project_name=None,
            result=result,
        )


def test_service_lists_today_and_counts_failures(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    failure = ExecutionResult(
        status=ExecutionStatus.FAILED,
        message="Falhou.",
        command="false",
        return_code=1,
    )
    service.record_execution(
        session_id="session-1",
        user_request="Falhe",
        working_directory="/tmp",
        project_name=None,
        result=failure,
    )

    now = datetime.now(UTC)

    assert len(service.executions_today(now=now)) == 1
    assert service.count_failures_today(now=now) == 1


def test_service_normalizes_path_working_directory(tmp_path: Path) -> None:
    service = build_service(tmp_path)
    working_directory = tmp_path / "project"
    result = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        message="Executado.",
        command="pwd",
        return_code=0,
        stdout=str(working_directory),
    )

    record = service.record_execution(
        session_id="session-1",
        user_request="Mostre o diretório atual",
        working_directory=working_directory,
        project_name="project",
        result=result,
    )

    assert record.working_directory == str(working_directory)
    assert service.last_execution() == record
