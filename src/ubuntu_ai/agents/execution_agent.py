from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from ubuntu_ai.agents.base import BaseAgent
from ubuntu_ai.agents.models import AgentKind, AgentResult, AgentTask


@dataclass(frozen=True, slots=True)
class ExecutionAgentPayload:
    action: Callable[[], object]


class ExecutionAgent(BaseAgent):
    kind = AgentKind.EXECUTION

    def handle(self, task: AgentTask) -> AgentResult:
        payload = task.payload
        if not isinstance(payload, ExecutionAgentPayload):
            raise TypeError("Payload inválido para ExecutionAgent.")

        result = payload.action()

        return AgentResult(
            kind=self.kind,
            output=result,
        )
