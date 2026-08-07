from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.agents.base import BaseAgent
from ubuntu_ai.agents.models import AgentKind, AgentResult, AgentTask
from ubuntu_ai.memory_intelligence.engine import MemoryIntelligenceEngine
from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryQuery,
)


@dataclass(frozen=True, slots=True)
class MemoryAgentPayload:
    query: MemoryQuery
    candidates: tuple[MemoryCandidate, ...]


class MemoryAgent(BaseAgent):
    kind = AgentKind.MEMORY

    def __init__(
        self,
        engine: MemoryIntelligenceEngine | None = None,
    ) -> None:
        self._engine = engine or MemoryIntelligenceEngine()

    def handle(self, task: AgentTask) -> AgentResult:
        payload = task.payload
        if not isinstance(payload, MemoryAgentPayload):
            raise TypeError("Payload inválido para MemoryAgent.")

        selection = self._engine.select(
            query=payload.query,
            candidates=payload.candidates,
        )

        return AgentResult(
            kind=self.kind,
            output=selection,
        )
