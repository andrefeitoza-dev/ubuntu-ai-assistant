from __future__ import annotations

from ubuntu_ai.memory_intelligence.models import MemorySelection


class MemoryPromptBuilder:
    """Formata uma seleção de memória para consumo por planejadores."""

    def build(self, selection: MemorySelection) -> str | None:
        if selection.is_empty():
            return None
        return selection.to_prompt()
