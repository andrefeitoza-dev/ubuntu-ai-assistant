from dataclasses import dataclass

from ubuntu_ai.agents.factory import build_default_agent_coordinator
from ubuntu_ai.reflection.failure import FailureKind
from ubuntu_ai.runtime_integration.reflection_bridge import (
    RuntimeReflectionBridge,
)


@dataclass
class FakeStatus:
    value: str


@dataclass
class FakeExecution:
    status: FakeStatus
    message: str = ""
    stdout: str = ""
    stderr: str = ""


class FakePlanner:
    def create_plan(self, request, context=None):
        return "plan"


def test_reflection_bridge_uses_reflection_agent() -> None:
    coordinator = build_default_agent_coordinator(planner=FakePlanner())

    report = RuntimeReflectionBridge(coordinator).reflect(
        FakeExecution(
            status=FakeStatus("failed"),
            stderr="Permission denied",
        )
    )

    assert report.failure.kind is FailureKind.PERMISSION
