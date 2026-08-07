from __future__ import annotations

from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.reflection.v2 import ReflectionV2Report


class RuntimeReflectionBridge:
    """Executa reflexão pós-execução através do ReflectionAgent."""

    def __init__(self, coordinator: AgentCoordinator) -> None:
        self._coordinator = coordinator

    def reflect(self, execution_result: object) -> ReflectionV2Report:
        result = self._coordinator.dispatch(
            AgentTask(
                kind=AgentKind.REFLECTION,
                payload=execution_result,
            )
        )

        if not isinstance(result.output, ReflectionV2Report):
            raise TypeError("ReflectionAgent retornou resultado inválido.")

        return result.output
