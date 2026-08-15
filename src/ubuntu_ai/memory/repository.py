from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ubuntu_ai.memory.models import ExecutionRecord


class MemoryRepository(Protocol):
    """Contrato de persistência do mecanismo de memória."""

    def save_execution(self, record: ExecutionRecord) -> None:
        """Persiste um registro de execução."""

    def get_execution(self, record_id: str) -> ExecutionRecord | None:
        """Busca um registro pelo identificador."""

    def get_last_execution(self) -> ExecutionRecord | None:
        """Retorna a execução persistida mais recente."""

    def list_executions(
        self,
        *,
        limit: int = 50,
        since: datetime | None = None,
        status: str | None = None,
        project_name: str | None = None,
    ) -> tuple[ExecutionRecord, ...]:
        """Lista execuções da mais recente para a mais antiga."""

    def count_executions(
        self,
        *,
        since: datetime | None = None,
        status: str | None = None,
    ) -> int:
        """Conta execuções usando filtros opcionais."""
