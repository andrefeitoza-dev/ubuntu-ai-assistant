from ubuntu_ai.memory_intelligence.engine import MemoryIntelligenceEngine
from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
    MemoryQuery,
)


def test_engine_consolidates_and_selects() -> None:
    candidates = (
        MemoryCandidate(
            kind=MemoryKind.PROJECT,
            content="package_manager=uv",
            project_name="ubuntu-ai",
            similarity=0.9,
        ),
        MemoryCandidate(
            kind=MemoryKind.PROJECT,
            content="package_manager=uv",
            project_name="ubuntu-ai",
            similarity=0.8,
        ),
        MemoryCandidate(
            kind=MemoryKind.EXECUTION,
            content="apt install foo",
            project_name="other",
            similarity=0.1,
        ),
    )

    selection = MemoryIntelligenceEngine().select(
        query=MemoryQuery(
            text="qual gerenciador usar",
            project_name="ubuntu-ai",
            limit=2,
        ),
        candidates=candidates,
    )

    assert len(selection.items) == 2
    assert selection.items[0].candidate.content == "package_manager=uv"
