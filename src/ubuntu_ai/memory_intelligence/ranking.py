from __future__ import annotations

from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryQuery,
    RankedMemory,
)


class MemoryRanker:
    """Calcula relevância combinando similaridade, contexto e histórico."""

    def rank(
        self,
        candidate: MemoryCandidate,
        query: MemoryQuery,
    ) -> RankedMemory:
        score = 0.0
        reasons: list[str] = []

        score += max(0.0, min(candidate.similarity, 1.0)) * 0.45
        if candidate.similarity > 0:
            reasons.append("similaridade semântica")

        score += max(0.0, min(candidate.importance, 1.0)) * 0.2
        if candidate.importance >= 0.7:
            reasons.append("alta importância")

        score += max(0.0, min(candidate.recency, 1.0)) * 0.15
        if candidate.recency >= 0.7:
            reasons.append("memória recente")

        success = max(-1.0, min(candidate.success_signal, 1.0))
        if success > 0:
            score += success * 0.1
            reasons.append("histórico favorável")
        elif success < 0:
            score += success * 0.05
            reasons.append("histórico de falha")

        if (
            query.project_name
            and candidate.project_name
            and query.project_name == candidate.project_name
        ):
            score += 0.1
            reasons.append("mesmo projeto")

        return RankedMemory(
            candidate=candidate,
            score=round(max(0.0, min(score, 1.0)), 4),
            reasons=tuple(reasons),
        )
