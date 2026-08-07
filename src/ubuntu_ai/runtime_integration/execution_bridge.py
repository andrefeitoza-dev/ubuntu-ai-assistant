from __future__ import annotations

from collections.abc import Callable

from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.agents.execution_agent import ExecutionAgentPayload
from ubuntu_ai.agents.models import AgentKind, AgentTask


class RuntimeExecutionBridge:
    """Executa uma ação através do ExecutionAgent."""

    def __init__(self, coordinator: AgentCoordinator) -> None:
        self._coordinator = coordinator

    def execute(
        self,
        action: Callable[[], object],
    ) -> object:
        result = self._coordinator.dispatch(
            AgentTask(
                kind=AgentKind.EXECUTION,
                payload=ExecutionAgentPayload(action=action),
            )
        )
        return result.output
