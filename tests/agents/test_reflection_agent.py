from dataclasses import dataclass

from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.agents.reflection_agent import ReflectionAgent
from ubuntu_ai.reflection.failure import FailureKind


@dataclass
class FakeStatus:
    value: str


@dataclass
class FakeExecution:
    status: FakeStatus
    message: str = ""
    stdout: str = ""
    stderr: str = ""


def test_reflection_agent_uses_reflection_v2() -> None:
    result = ReflectionAgent().handle(
        AgentTask(
            kind=AgentKind.REFLECTION,
            payload=FakeExecution(
                status=FakeStatus("failed"),
                stderr="Permission denied",
            ),
        )
    )

    assert result.output.failure.kind is FailureKind.PERMISSION
