from ubuntu_ai.memory_intelligence.models import MemoryKind
from ubuntu_ai.memory_intelligence.project_memory import (
    ProjectFact,
    ProjectMemoryBuilder,
)


def test_project_fact_becomes_memory_candidate() -> None:
    candidate = ProjectMemoryBuilder().build(
        ProjectFact(
            project_name="ubuntu-ai",
            key="package_manager",
            value="uv",
            confidence=0.95,
        )
    )

    assert candidate.kind is MemoryKind.PROJECT
    assert candidate.project_name == "ubuntu-ai"
    assert candidate.content == "package_manager=uv"
    assert candidate.importance == 0.95
