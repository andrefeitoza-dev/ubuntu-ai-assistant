from __future__ import annotations

from collections.abc import Iterable

from ubuntu_ai.memory_intelligence.consolidation import MemoryConsolidator
from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryQuery,
    MemorySelection,
)
from ubuntu_ai.memory_intelligence.retrieval import MemoryRetrievalEngine


class MemoryIntelligenceEngine:
    """Orquestra consolidação e recuperação inteligente de memórias."""

    def __init__(
        self,
        consolidator: MemoryConsolidator | None = None,
        retrieval: MemoryRetrievalEngine | None = None,
    ) -> None:
        self._consolidator = consolidator or MemoryConsolidator()
        self._retrieval = retrieval or MemoryRetrievalEngine()

    def select(
        self,
        *,
        query: MemoryQuery,
        candidates: Iterable[MemoryCandidate],
    ) -> MemorySelection:
        consolidated = self._consolidator.consolidate(tuple(candidates))
        return self._retrieval.retrieve(query, consolidated)
