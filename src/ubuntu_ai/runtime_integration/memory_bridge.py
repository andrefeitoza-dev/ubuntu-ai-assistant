from __future__ import annotations

from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.agents.memory_agent import MemoryAgentPayload
from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.memory.service import MemoryService
from ubuntu_ai.memory_intelligence.execution_memory import ExecutionMemoryBuilder
from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryQuery,
    MemorySelection,
)


class RuntimeMemoryBridge:
    """Consulta o MemoryAgent usando o contexto e candidatos fornecidos."""

    def __init__(
        self,
        coordinator: AgentCoordinator,
        memory_service: MemoryService | None = None,
    ) -> None:
        self._coordinator = coordinator
        self._memory_service = memory_service
        self._execution_memory_builder = ExecutionMemoryBuilder()

    def select(
        self,
        *,
        request_text: str,
        context: ContextSnapshot | None,
        candidates: tuple[MemoryCandidate, ...],
        limit: int = 5,
    ) -> MemorySelection:
        project_name = context.project_name if context is not None else None

        persisted_candidates: tuple[MemoryCandidate, ...] = ()

        if self._memory_service is not None:
            records = self._memory_service.recent_executions(
                limit=20,
                project_name=project_name,
            )
            persisted_candidates = tuple(
                self._execution_memory_builder.build(record) for record in records
            )

        all_candidates = candidates + persisted_candidates

        if not all_candidates:
            return MemorySelection()

        result = self._coordinator.dispatch(
            AgentTask(
                kind=AgentKind.MEMORY,
                payload=MemoryAgentPayload(
                    query=MemoryQuery(
                        text=request_text,
                        project_name=project_name,
                        limit=limit,
                    ),
                    candidates=all_candidates,
                ),
            )
        )

        if not isinstance(result.output, MemorySelection):
            raise TypeError("MemoryAgent retornou resultado inválido.")

        return result.output
