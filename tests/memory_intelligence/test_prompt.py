from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
    MemorySelection,
    RankedMemory,
)
from ubuntu_ai.memory_intelligence.prompt import MemoryPromptBuilder


def test_prompt_builder_returns_none_for_empty_selection() -> None:
    assert MemoryPromptBuilder().build(MemorySelection()) is None


def test_prompt_builder_returns_memory_context() -> None:
    selection = MemorySelection(
        items=(
            RankedMemory(
                candidate=MemoryCandidate(
                    kind=MemoryKind.LEARNING,
                    content="prefira uv",
                ),
                score=0.8,
            ),
        )
    )

    prompt = MemoryPromptBuilder().build(selection)

    assert prompt is not None
    assert "prefira uv" in prompt
