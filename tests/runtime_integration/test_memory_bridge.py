from ubuntu_ai.agents.factory import build_default_agent_coordinator
from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
)
from ubuntu_ai.runtime_integration.memory_bridge import RuntimeMemoryBridge


class FakePlanner:
    def create_plan(self, request, context=None):
        return "plan"


def test_memory_bridge_selects_candidate() -> None:
    coordinator = build_default_agent_coordinator(
        planner=FakePlanner()
    )

    selection = RuntimeMemoryBridge(coordinator).select(
        request_text="uv",
        context=None,
        candidates=(
            MemoryCandidate(
                kind=MemoryKind.PROJECT,
                content="package_manager=uv",
                similarity=0.9,
            ),
        ),
    )

    assert len(selection.items) == 1
