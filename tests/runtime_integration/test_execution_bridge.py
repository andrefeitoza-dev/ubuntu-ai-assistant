from ubuntu_ai.agents.factory import build_default_agent_coordinator
from ubuntu_ai.runtime_integration.execution_bridge import (
    RuntimeExecutionBridge,
)


class FakePlanner:
    def create_plan(self, request, context=None):
        return "plan"


def test_execution_bridge_runs_action() -> None:
    coordinator = build_default_agent_coordinator(planner=FakePlanner())

    result = RuntimeExecutionBridge(coordinator).execute(lambda: "executed")

    assert result == "executed"
