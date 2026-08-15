from __future__ import annotations

from datetime import UTC, datetime, time, timedelta
from os import PathLike

from ubuntu_ai.execution.models import ExecutionResult
from ubuntu_ai.memory.models import ExecutionRecord
from ubuntu_ai.memory.repository import MemoryRepository


class MemoryService:
    """Serviço de aplicação para gravação e consulta da memória."""

    def __init__(self, repository: MemoryRepository) -> None:
        self._repository = repository

    def record_execution(
        self,
        *,
        session_id: str,
        user_request: str,
        working_directory: str | PathLike[str],
        project_name: str | None,
        result: ExecutionResult,
    ) -> ExecutionRecord:
        """Transforma um resultado de execução em memória persistente."""

        command = result.command
        if command is None:
            raise ValueError("O resultado precisa conter o comando executado.")

        record = ExecutionRecord.create(
            session_id=session_id,
            user_request=user_request,
            command=command,
            status=result.status.value,
            message=result.message,
            working_directory=str(working_directory),
            project_name=project_name,
            return_code=result.return_code,
            stdout=result.stdout,
            stderr=result.stderr,
            duration=result.duration,
        )
        self._repository.save_execution(record)
        return record

    def last_execution(self) -> ExecutionRecord | None:
        """Retorna a execução persistida mais recente."""

        return self._repository.get_last_execution()

    def recent_executions(
        self,
        *,
        limit: int = 50,
        status: str | None = None,
        project_name: str | None = None,
    ) -> tuple[ExecutionRecord, ...]:
        """Retorna execuções recentes usando filtros opcionais."""

        return self._repository.list_executions(
            limit=limit,
            status=status,
            project_name=project_name,
        )

    def executions_today(
        self,
        *,
        now: datetime | None = None,
        limit: int = 100,
    ) -> tuple[ExecutionRecord, ...]:
        """Retorna execuções registradas desde o início do dia atual."""

        reference = now or datetime.now(UTC)
        start_of_day = datetime.combine(
            reference.date(),
            time.min,
            tzinfo=reference.tzinfo or UTC,
        )

        return self._repository.list_executions(
            limit=limit,
            since=start_of_day,
        )

    def count_failures_today(self, *, now: datetime | None = None) -> int:
        """Conta falhas registradas desde o início do dia atual."""

        reference = now or datetime.now(UTC)
        start_of_day = datetime.combine(
            reference.date(),
            time.min,
            tzinfo=reference.tzinfo or UTC,
        )

        return self._repository.count_executions(
            since=start_of_day,
            status="failed",
        )

    def executions_since(
        self,
        *,
        days: int,
        limit: int = 100,
    ) -> tuple[ExecutionRecord, ...]:
        """Retorna execuções ocorridas nos últimos dias."""

        if days < 1:
            raise ValueError("A quantidade de dias deve ser maior que zero.")

        since = datetime.now(UTC) - timedelta(days=days)
        return self._repository.list_executions(limit=limit, since=since)
