from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class MemoryEventType(StrEnum):
    """Tipos de eventos persistidos pelo mecanismo de memória."""

    EXECUTION = "execution"


@dataclass(slots=True, frozen=True)
class ExecutionRecord:
    """Registro persistente de uma tentativa de execução."""

    id: str
    created_at: datetime
    session_id: str
    user_request: str
    command: str
    status: str
    message: str
    working_directory: str
    project_name: str | None = None
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration: float | None = None
    event_type: MemoryEventType = MemoryEventType.EXECUTION

    @classmethod
    def create(
        cls,
        *,
        session_id: str,
        user_request: str,
        command: str,
        status: str,
        message: str,
        working_directory: str,
        project_name: str | None = None,
        return_code: int | None = None,
        stdout: str = "",
        stderr: str = "",
        duration: float | None = None,
    ) -> ExecutionRecord:
        """Cria um registro com identificador e horário em UTC."""

        return cls(
            id=str(uuid4()),
            created_at=datetime.now(UTC),
            session_id=session_id,
            user_request=user_request,
            command=command,
            status=status,
            message=message,
            working_directory=working_directory,
            project_name=project_name,
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
            duration=duration,
        )
