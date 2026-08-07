from __future__ import annotations

from ubuntu_ai.agents.memory_agent import MemoryAgentPayload
from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryQuery,
    MemorySelection,
)


class RuntimeMemoryBridge:
    """Consulta o MemoryAgent usando o contexto e candidatos fornecidos."""

    def __init__(self, coordinator: AgentCoordinator) -> None:
        self._coordinator = coordinator

    def select(
        self,
        *,
        request_text: str,
        context: ContextSnapshot | None,
        candidates: tuple[MemoryCandidate, ...],
        limit: int = 5,
    ) -> MemorySelection:
        if not candidates:
            return MemorySelection()

        project_name = context.project_name if context is not None else None

        result = self._coordinator.dispatch(
            AgentTask(
                kind=AgentKind.MEMORY,
                payload=MemoryAgentPayload(
                    query=MemoryQuery(
                        text=request_text,
                        project_name=project_name,
                        limit=limit,
                    ),
                    candidates=candidates,
                ),
            )
        )

        if not isinstance(result.output, MemorySelection):
            raise TypeError("MemoryAgent retornou resultado inválido.")

        return result.output
