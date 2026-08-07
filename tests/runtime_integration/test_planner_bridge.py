from ubuntu_ai.agents.factory import build_default_agent_coordinator
from ubuntu_ai.runtime_integration.planner_bridge import RuntimePlannerBridge


class FakePlanner:
    def create_plan(self, request, context=None):
        return f"plan:{request}"


def test_planner_bridge_dispatches_to_planner_agent() -> None:
    coordinator = build_default_agent_coordinator(
        planner=FakePlanner()
    )

    plan = RuntimePlannerBridge(coordinator).create_plan(
        request="status",
        context=None,
    )

    assert plan == "plan:status"
