from ubuntu_ai.memory_intelligence.consolidation import MemoryConsolidator
from ubuntu_ai.memory_intelligence.models import MemoryCandidate, MemoryKind


def test_duplicate_memories_are_consolidated() -> None:
    candidates = (
        MemoryCandidate(
            kind=MemoryKind.PROJECT,
            content="Package Manager = uv",
            project_name="ubuntu-ai",
            importance=0.6,
            recency=0.4,
        ),
        MemoryCandidate(
            kind=MemoryKind.PROJECT,
            content="package   manager = UV",
            project_name="ubuntu-ai",
            importance=0.8,
            recency=0.9,
        ),
    )

    result = MemoryConsolidator().consolidate(candidates)

    assert len(result) == 1
    assert result[0].importance >= 0.8
    assert result[0].recency == 0.9
