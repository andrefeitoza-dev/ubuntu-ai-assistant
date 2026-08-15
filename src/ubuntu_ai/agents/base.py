from __future__ import annotations

from abc import ABC, abstractmethod

from ubuntu_ai.agents.models import AgentKind, AgentResult, AgentTask


class BaseAgent(ABC):
    """Contrato comum para agentes especializados."""

    kind: AgentKind

    @abstractmethod
    def handle(self, task: AgentTask) -> AgentResult:
        """Executa uma tarefa compatível com o agente."""
