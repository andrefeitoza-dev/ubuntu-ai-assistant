import pytest

from ubuntu_ai.agents.base import BaseAgent
from ubuntu_ai.agents.models import AgentKind, AgentResult, AgentTask
from ubuntu_ai.agents.registry import AgentRegistry


class FakeAgent(BaseAgent):
    kind = AgentKind.MEMORY

    def handle(self, task: AgentTask) -> AgentResult:
        return AgentResult(kind=self.kind, output=task.payload)


def test_registry_registers_and_gets_agent() -> None:
    registry = AgentRegistry()
    agent = FakeAgent()

    registry.register(agent)

    assert registry.get(AgentKind.MEMORY) is agent


def test_registry_rejects_duplicate() -> None:
    registry = AgentRegistry()
    registry.register(FakeAgent())

    with pytest.raises(ValueError):
        registry.register(FakeAgent())
