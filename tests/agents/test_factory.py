from ubuntu_ai.agents.factory import build_default_agent_coordinator
from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.agents.planner_agent import PlannerAgentPayload


class FakePlanner:
    def create_plan(self, request, context=None):
        return f"plan:{request}"


def test_factory_builds_default_multi_agent_runtime() -> None:
    coordinator = build_default_agent_coordinator(planner=FakePlanner())

    result = coordinator.dispatch(
        AgentTask(
            kind=AgentKind.PLANNER,
            payload=PlannerAgentPayload(request="status"),
        )
    )

    assert result.output == "plan:status"


def test_factory_registers_domain_specialists() -> None:
    coordinator = build_default_agent_coordinator(planner=FakePlanner())

    for kind in (
        AgentKind.SYSTEM,
        AgentKind.NETWORK,
        AgentKind.STORAGE,
        AgentKind.SERVICES,
    ):
        assert coordinator.registry.get(kind).kind is kind
