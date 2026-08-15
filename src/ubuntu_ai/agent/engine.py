from ubuntu_ai.agent.models import AgentResult, AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime


class AgentEngine:
    """Fachada de alto nível para execução do agente."""

    def __init__(
        self,
        runtime: AgentRuntime | None = None,
    ) -> None:
        self._runtime = runtime or AgentRuntime()

    def run(self, task: AgentTask) -> AgentResult:
        return self._runtime.run(task)
