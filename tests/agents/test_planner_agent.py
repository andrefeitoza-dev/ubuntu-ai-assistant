from dataclasses import dataclass

from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.agents.planner_agent import PlannerAgent, PlannerAgentPayload


@dataclass
class FakePlanner:
    last_request: object | None = None

    def create_plan(self, request, context=None):
        self.last_request = request
        return "plan"


def test_planner_agent_delegates_to_planner() -> None:
    planner = FakePlanner()
    agent = PlannerAgent(planner)

    result = agent.handle(
        AgentTask(
            kind=AgentKind.PLANNER,
            payload=PlannerAgentPayload(
                request="instale docker",
                context=None,
            ),
        )
    )

    assert result.output == "plan"
    assert planner.last_request == "instale docker"
