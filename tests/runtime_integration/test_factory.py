from ubuntu_ai.runtime_integration.factory import build_multi_agent_runtime
from ubuntu_ai.runtime_integration.models import RuntimeRequest, RuntimeStage


class FakePlanner:
    def create_plan(self, request, context=None):
        return f"plan:{request}"


def test_factory_builds_runtime() -> None:
    runtime = build_multi_agent_runtime(planner=FakePlanner())

    result = runtime.run(
        RuntimeRequest(
            request="status",
            session_id="s",
        )
    )

    assert result.stage is RuntimeStage.PLANNING
    assert result.plan == "plan:status"
