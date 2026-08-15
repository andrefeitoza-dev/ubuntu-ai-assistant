from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
)


@dataclass(frozen=True, slots=True)
class ProjectFact:
    """Fato persistível aprendido sobre um projeto."""

    project_name: str
    key: str
    value: str
    confidence: float = 0.8


class ProjectMemoryBuilder:
    """Converte fatos de projeto em memórias recuperáveis."""

    def build(self, fact: ProjectFact) -> MemoryCandidate:
        return MemoryCandidate(
            kind=MemoryKind.PROJECT,
            content=f"{fact.key}={fact.value}",
            project_name=fact.project_name,
            importance=max(0.0, min(fact.confidence, 1.0)),
            recency=1.0,
            similarity=0.0,
            source="project_fact",
        )
