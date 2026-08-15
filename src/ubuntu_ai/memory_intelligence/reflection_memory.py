from __future__ import annotations

from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
)
from ubuntu_ai.reflection.v2 import ReflectionV2Report


class ReflectionMemoryBuilder:
    """Converte reflexões pós-execução em memória recuperável."""

    def build(
        self,
        *,
        report: ReflectionV2Report,
        project_name: str | None = None,
    ) -> MemoryCandidate:
        return MemoryCandidate(
            kind=MemoryKind.LEARNING,
            content=report.summary(),
            project_name=project_name,
            importance=0.8,
            recency=1.0,
            similarity=0.0,
            success_signal=1.0 if report.retry_allowed else 0.0,
            source="reflection",
        )
