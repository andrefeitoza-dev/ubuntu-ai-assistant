from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.agents.base import BaseAgent
from ubuntu_ai.agents.models import AgentKind, AgentResult, AgentTask
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.memory_intelligence.models import MemorySelection
from ubuntu_ai.planner.planner import Planner


@dataclass(frozen=True, slots=True)
class PlannerAgentPayload:
    request: object
    context: ContextSnapshot | None = None
    memory: MemorySelection | None = None


class PlannerAgent(BaseAgent):
    kind = AgentKind.PLANNER

    def __init__(self, planner: Planner) -> None:
        self._planner = planner

    def handle(self, task: AgentTask) -> AgentResult:
        payload = task.payload

        if not isinstance(payload, PlannerAgentPayload):
            raise TypeError("Payload inválido para PlannerAgent.")

        if payload.memory is None or payload.memory.is_empty():
            plan = self._planner.create_plan(
                payload.request,
                context=payload.context,
            )
        else:
            plan = self._planner.create_plan(
                payload.request,
                context=payload.context,
                memory=payload.memory,
            )

        return AgentResult(
            kind=self.kind,
            output=plan,
        )
