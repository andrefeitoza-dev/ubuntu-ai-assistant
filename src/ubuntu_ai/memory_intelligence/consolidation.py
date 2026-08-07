from __future__ import annotations

from collections import defaultdict
from dataclasses import replace

from ubuntu_ai.memory_intelligence.models import MemoryCandidate, MemoryKind


class MemoryConsolidator:
    """Consolida memórias repetidas sem depender de um backend específico."""

    def consolidate(
        self,
        candidates: tuple[MemoryCandidate, ...],
    ) -> tuple[MemoryCandidate, ...]:
        groups: dict[
            tuple[MemoryKind, str | None, str],
            list[MemoryCandidate],
        ] = defaultdict(list)

        for candidate in candidates:
            normalized = " ".join(candidate.content.lower().split())
            key = (
                candidate.kind,
                candidate.project_name,
                normalized,
            )
            groups[key].append(candidate)

        consolidated: list[MemoryCandidate] = []

        for items in groups.values():
            best = max(
                items,
                key=lambda item: (
                    item.importance,
                    item.recency,
                    item.similarity,
                ),
            )

            if len(items) == 1:
                consolidated.append(best)
                continue

            consolidated.append(
                replace(
                    best,
                    importance=min(
                        1.0,
                        max(item.importance for item in items)
                        + min(0.2, 0.05 * (len(items) - 1)),
                    ),
                    recency=max(item.recency for item in items),
                    success_signal=max(
                        item.success_signal for item in items
                    ),
                )
            )

        return tuple(consolidated)
