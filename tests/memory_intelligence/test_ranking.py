from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
    MemoryQuery,
)
from ubuntu_ai.memory_intelligence.ranking import MemoryRanker


def test_same_project_increases_score() -> None:
    ranker = MemoryRanker()
    candidate = MemoryCandidate(
        kind=MemoryKind.EXECUTION,
        content="uv run pytest",
        project_name="ubuntu-ai",
        importance=0.8,
        recency=0.8,
        similarity=0.8,
        success_signal=1.0,
    )

    same = ranker.rank(
        candidate,
        MemoryQuery(
            text="rodar testes",
            project_name="ubuntu-ai",
        ),
    )
    other = ranker.rank(
        candidate,
        MemoryQuery(
            text="rodar testes",
            project_name="other",
        ),
    )

    assert same.score > other.score
    assert "mesmo projeto" in same.reasons


def test_failure_signal_penalizes_score() -> None:
    ranker = MemoryRanker()

    good = ranker.rank(
        MemoryCandidate(
            kind=MemoryKind.EXECUTION,
            content="docker compose up",
            similarity=0.5,
            success_signal=1.0,
        ),
        MemoryQuery(text="docker"),
    )
    bad = ranker.rank(
        MemoryCandidate(
            kind=MemoryKind.EXECUTION,
            content="docker compose up",
            similarity=0.5,
            success_signal=-1.0,
        ),
        MemoryQuery(text="docker"),
    )

    assert good.score > bad.score
