from dataclasses import dataclass

from ubuntu_ai.agents.factory import build_default_agent_coordinator
from ubuntu_ai.runtime_integration.context_builder import RuntimeContextBuilder
from ubuntu_ai.runtime_integration.execution_bridge import RuntimeExecutionBridge
from ubuntu_ai.runtime_integration.memory_bridge import RuntimeMemoryBridge
from ubuntu_ai.runtime_integration.models import (
    RuntimeRequest,
    RuntimeStage,
)
from ubuntu_ai.runtime_integration.planner_bridge import RuntimePlannerBridge
from ubuntu_ai.runtime_integration.reflection_bridge import RuntimeReflectionBridge
from ubuntu_ai.runtime_integration.workflow import RuntimeWorkflow


class FakePlanner:
    def create_plan(self, request, context=None):
        return f"plan:{request}"


@dataclass
class FakeStatus:
    value: str


@dataclass
class FakeExecution:
    status: FakeStatus
    message: str = ""
    stdout: str = ""
    stderr: str = ""


def build_workflow() -> RuntimeWorkflow:
    coordinator = build_default_agent_coordinator(
        planner=FakePlanner()
    )

    return RuntimeWorkflow(
        context_builder=RuntimeContextBuilder(),
        memory_bridge=RuntimeMemoryBridge(coordinator),
        planner_bridge=RuntimePlannerBridge(coordinator),
        execution_bridge=RuntimeExecutionBridge(coordinator),
        reflection_bridge=RuntimeReflectionBridge(coordinator),
    )


def test_workflow_can_stop_after_planning() -> None:
    result = build_workflow().run(
        RuntimeRequest(
            request="status",
            session_id="s",
            execute=False,
        )
    )

    assert result.stage is RuntimeStage.PLANNING
    assert result.plan == "plan:status"


def test_workflow_executes_and_reflects() -> None:
    result = build_workflow().run(
        RuntimeRequest(
            request="status",
            session_id="s",
            execute=True,
        ),
        execution_action=lambda plan: FakeExecution(
            status=FakeStatus("failed"),
            stderr="Connection refused",
        ),
    )

    assert result.stage is RuntimeStage.COMPLETED
    assert result.execution is not None
    assert result.reflection is not None
