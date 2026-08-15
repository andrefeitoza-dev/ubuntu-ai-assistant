from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
    MemorySelection,
    RankedMemory,
)


def test_memory_selection_renders_prompt() -> None:
    selection = MemorySelection(
        items=(
            RankedMemory(
                candidate=MemoryCandidate(
                    kind=MemoryKind.PROJECT,
                    content="package_manager=uv",
                    project_name="ubuntu-ai",
                    source="project_fact",
                ),
                score=0.91,
                reasons=("mesmo projeto",),
            ),
        )
    )

    prompt = selection.to_prompt()

    assert "Memórias relevantes:" in prompt
    assert "project" in prompt
    assert "package_manager=uv" in prompt
    assert "0.91" in prompt
