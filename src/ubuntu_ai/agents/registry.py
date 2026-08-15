from __future__ import annotations

from ubuntu_ai.agents.base import BaseAgent
from ubuntu_ai.agents.models import AgentKind


class AgentRegistry:
    """Registro de agentes especializados."""

    def __init__(self) -> None:
        self._agents: dict[AgentKind, BaseAgent] = {}

    def register(
        self,
        agent: BaseAgent,
        *,
        replace: bool = False,
    ) -> None:
        if agent.kind in self._agents and not replace:
            raise ValueError(f"Agente já registrado: {agent.kind.value}")
        self._agents[agent.kind] = agent

    def get(self, kind: AgentKind) -> BaseAgent:
        try:
            return self._agents[kind]
        except KeyError as exc:
            raise KeyError(f"Agente não registrado: {kind.value}") from exc

    def all(self) -> tuple[BaseAgent, ...]:
        return tuple(
            self._agents[kind] for kind in sorted(self._agents, key=lambda item: item.value)
        )
