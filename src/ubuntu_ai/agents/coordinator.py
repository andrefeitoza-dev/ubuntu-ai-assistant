from __future__ import annotations

from ubuntu_ai.agents.models import AgentResult, AgentTask
from ubuntu_ai.agents.policy import AgentPolicy
from ubuntu_ai.agents.registry import AgentRegistry
from ubuntu_ai.agents.router import AgentRouter


class AgentCoordinator:
    """Coordena despacho seguro de tarefas entre agentes especializados."""

    def __init__(
        self,
        registry: AgentRegistry,
        router: AgentRouter | None = None,
        policy: AgentPolicy | None = None,
    ) -> None:
        self._registry = registry
        self._router = router or AgentRouter()
        self._policy = policy or AgentPolicy()

    @property
    def registry(self) -> AgentRegistry:
        return self._registry

    def dispatch(self, task: AgentTask) -> AgentResult:
        decision = self._policy.evaluate(task)

        if not decision.allowed:
            raise PermissionError(decision.reason)

        kind = self._router.route(task)
        agent = self._registry.get(kind)
        return agent.handle(task)
