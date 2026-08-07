from __future__ import annotations

from ubuntu_ai.agents.models import AgentKind, AgentTask


class AgentRouter:
    """Determina qual agente deve receber uma tarefa."""

    def route(self, task: AgentTask) -> AgentKind:
        return task.kind
