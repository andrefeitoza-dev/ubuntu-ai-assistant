from __future__ import annotations

from ubuntu_ai.memory.models import ExecutionRecord
from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
)


class ExecutionMemoryBuilder:
    """Converte execuções persistidas em memórias recuperáveis."""

    def build(self, record: ExecutionRecord) -> MemoryCandidate:
        success = record.status == "executed"

        content = (
            f"Pedido: {record.user_request}; "
            f"comando: {record.command}; "
            f"status: {record.status}; "
            f"resultado: {record.message}"
        )

        return MemoryCandidate(
            kind=MemoryKind.EXECUTION,
            content=content,
            project_name=record.project_name,
            importance=0.8 if success else 0.6,
            recency=1.0,
            similarity=0.0,
            success_signal=1.0 if success else 0.0,
            source="execution_history",
        )
