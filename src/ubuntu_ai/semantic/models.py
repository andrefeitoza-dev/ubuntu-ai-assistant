from __future__ import annotations

from dataclasses import dataclass, field

from ubuntu_ai.knowledge.models import KnowledgeChunk, KnowledgeDocument


@dataclass(frozen=True, slots=True)
class SemanticMatch:
    """Trecho recuperado por similaridade semântica local."""

    document: KnowledgeDocument
    chunk: KnowledgeChunk
    score: float
    lexical_score: float = 0.0
    semantic_score: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (
            ("score", self.score),
            ("lexical_score", self.lexical_score),
            ("semantic_score", self.semantic_score),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} deve estar entre 0 e 1.")


@dataclass(frozen=True, slots=True)
class RetrievalContext:
    """Contexto pronto para ser injetado em prompts do agente."""

    query: str
    matches: tuple[SemanticMatch, ...] = field(default_factory=tuple)

    @property
    def is_empty(self) -> bool:
        return not self.matches

    def to_prompt(self, *, max_chars: int = 4_000) -> str:
        if self.is_empty:
            return ""

        sections: list[str] = []
        current_size = 0
        for index, match in enumerate(self.matches, start=1):
            reference = match.document.source_reference or match.document.title
            section = (
                f"[{index}] {match.document.title} | fonte={reference} | "
                f"relevância={match.score:.3f}\n{match.chunk.content.strip()}"
            )
            projected = current_size + len(section) + 2
            if sections and projected > max_chars:
                break
            sections.append(section)
            current_size = projected

        return "\n\n".join(sections)
