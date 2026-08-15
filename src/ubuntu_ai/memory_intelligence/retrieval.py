from __future__ import annotations

from collections.abc import Iterable

from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryQuery,
    MemorySelection,
)
from ubuntu_ai.memory_intelligence.ranking import MemoryRanker


class MemoryRetrievalEngine:
    """Seleciona as memórias mais relevantes para uma consulta."""

    def __init__(self, ranker: MemoryRanker | None = None) -> None:
        self._ranker = ranker or MemoryRanker()

    def retrieve(
        self,
        query: MemoryQuery,
        candidates: Iterable[MemoryCandidate],
    ) -> MemorySelection:
        if query.limit < 1:
            raise ValueError("O limite de memórias deve ser maior que zero.")

        ranked = [self._ranker.rank(candidate, query) for candidate in candidates]
        ranked.sort(
            key=lambda item: item.score,
            reverse=True,
        )

        return MemorySelection(items=tuple(ranked[: query.limit]))
