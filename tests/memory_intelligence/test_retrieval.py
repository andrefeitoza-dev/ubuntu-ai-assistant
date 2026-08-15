import pytest

from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
    MemoryQuery,
)
from ubuntu_ai.memory_intelligence.retrieval import MemoryRetrievalEngine


def test_retrieval_respects_limit_and_order() -> None:
    candidates = (
        MemoryCandidate(
            kind=MemoryKind.KNOWLEDGE,
            content="low",
            similarity=0.1,
        ),
        MemoryCandidate(
            kind=MemoryKind.KNOWLEDGE,
            content="high",
            similarity=0.9,
        ),
        MemoryCandidate(
            kind=MemoryKind.KNOWLEDGE,
            content="medium",
            similarity=0.5,
        ),
    )

    selection = MemoryRetrievalEngine().retrieve(
        MemoryQuery(text="query", limit=2),
        candidates,
    )

    assert len(selection.items) == 2
    assert selection.items[0].candidate.content == "high"


def test_retrieval_rejects_invalid_limit() -> None:
    with pytest.raises(ValueError):
        MemoryRetrievalEngine().retrieve(
            MemoryQuery(text="query", limit=0),
            (),
        )
