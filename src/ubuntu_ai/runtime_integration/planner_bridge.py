from __future__ import annotations

from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.agents.planner_agent import PlannerAgentPayload
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.memory_intelligence.models import MemorySelection


class RuntimePlannerBridge:
    """Delega planejamento ao PlannerAgent registrado."""

    def __init__(self, coordinator: AgentCoordinator) -> None:
        self._coordinator = coordinator

    def create_plan(
        self,
        *,
        request: object,
        context: ContextSnapshot | None,
        memory: MemorySelection | None = None,
    ) -> object:
        result = self._coordinator.dispatch(
            AgentTask(
                kind=AgentKind.PLANNER,
                payload=PlannerAgentPayload(
                    request=request,
                    context=context,
                    memory=memory,
                ),
            )
        )
        return result.output
