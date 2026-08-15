from __future__ import annotations

from ubuntu_ai.agents.base import BaseAgent
from ubuntu_ai.agents.models import AgentKind, AgentResult, AgentTask
from ubuntu_ai.reflection.v2_service import ReflectionV2Service


class ReflectionAgent(BaseAgent):
    kind = AgentKind.REFLECTION

    def __init__(
        self,
        service: ReflectionV2Service | None = None,
    ) -> None:
        self._service = service or ReflectionV2Service()

    def handle(self, task: AgentTask) -> AgentResult:
        report = self._service.reflect_execution(task.payload)
        return AgentResult(
            kind=self.kind,
            output=report,
        )
