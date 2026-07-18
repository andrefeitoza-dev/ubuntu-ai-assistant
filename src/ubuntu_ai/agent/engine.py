from ubuntu_ai.agent.models import AgentResult, AgentTask


class AgentEngine:
    """Coordena o ciclo completo do agente."""

    def run(self, task: AgentTask) -> AgentResult:
        raise NotImplementedError