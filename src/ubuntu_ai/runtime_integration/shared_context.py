from __future__ import annotations

from dataclasses import dataclass, replace

from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.memory_intelligence.models import MemorySelection


@dataclass(frozen=True, slots=True)
class SharedAgentContext:
    """Contexto comum compartilhado entre os agentes."""

    snapshot: ContextSnapshot | None = None
    memory: MemorySelection | None = None

    def with_memory(
        self,
        memory: MemorySelection,
    ) -> SharedAgentContext:
        return replace(self, memory=memory)

    def memory_prompt(self) -> str | None:
        if self.memory is None or self.memory.is_empty():
            return None
        return self.memory.to_prompt()
