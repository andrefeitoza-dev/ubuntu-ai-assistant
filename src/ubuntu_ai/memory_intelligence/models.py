from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class MemoryKind(StrEnum):
    """Categorias de memória compreendidas pela camada inteligente."""

    EXECUTION = "execution"
    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    LEARNING = "learning"
    PROJECT = "project"


@dataclass(frozen=True, slots=True)
class MemoryQuery:
    """Consulta estruturada usada para recuperar memórias relevantes."""

    text: str
    project_name: str | None = None
    limit: int = 5


@dataclass(frozen=True, slots=True)
class MemoryCandidate:
    """Memória candidata a ser ranqueada."""

    kind: MemoryKind
    content: str
    project_name: str | None = None
    importance: float = 0.5
    recency: float = 0.5
    similarity: float = 0.0
    success_signal: float = 0.0
    source: str | None = None


@dataclass(frozen=True, slots=True)
class RankedMemory:
    """Memória ranqueada com score explicável."""

    candidate: MemoryCandidate
    score: float
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MemorySelection:
    """Resultado final da recuperação inteligente."""

    items: tuple[RankedMemory, ...] = ()

    def is_empty(self) -> bool:
        return not self.items

    def to_prompt(self) -> str:
        if not self.items:
            return ""

        lines = ["Memórias relevantes:"]
        for item in self.items:
            source = f" source={item.candidate.source}" if item.candidate.source else ""
            lines.append(
                f"- [{item.candidate.kind.value}] "
                f"score={item.score:.2f}{source}: "
                f"{item.candidate.content}"
            )
        return "\n".join(lines)
