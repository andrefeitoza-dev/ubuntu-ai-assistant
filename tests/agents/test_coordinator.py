import pytest

from ubuntu_ai.agents.base import BaseAgent
from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.agents.models import AgentKind, AgentResult, AgentTask
from ubuntu_ai.agents.registry import AgentRegistry


class FakeAgent(BaseAgent):
    kind = AgentKind.PLANNER

    def handle(self, task: AgentTask) -> AgentResult:
        return AgentResult(kind=self.kind, output="ok")


def test_coordinator_dispatches_task() -> None:
    registry = AgentRegistry()
    registry.register(FakeAgent())

    result = AgentCoordinator(registry).dispatch(
        AgentTask(kind=AgentKind.PLANNER, payload="request")
    )

    assert result.output == "ok"


def test_coordinator_enforces_policy() -> None:
    registry = AgentRegistry()

    with pytest.raises(PermissionError):
        AgentCoordinator(registry).dispatch(
            AgentTask(kind=AgentKind.EXECUTION, payload=None)
        )
