from dataclasses import dataclass
from pathlib import Path

from ubuntu_ai.agent.context import AgentContext
from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.domain.risk import RiskLevel


@dataclass
class FakePipelineResult:
    plan: Plan
    rendered_preview: str = "preview"


class ContextAwarePipeline:
    def __init__(self) -> None:
        self.context: ContextSnapshot | None = None

    def run(
        self,
        request: str,
        context: ContextSnapshot | None = None,
    ) -> FakePipelineResult:
        self.context = context
        return FakePipelineResult(
            plan=Plan(
                goal=request,
                estimated_seconds=1,
                risk=RiskLevel.LOW,
            )
        )


class FakeContextProvider:
    def get_context(self) -> AgentContext:
        return AgentContext(
            working_directory=Path("/tmp/project"),
            operating_system="Linux",
            project_name="project",
        )


def test_runtime_builds_and_forwards_context_snapshot() -> None:
    pipeline = ContextAwarePipeline()
    runtime = AgentRuntime(
        execution_pipeline=pipeline,  # type: ignore[arg-type]
        context_provider=FakeContextProvider(),  # type: ignore[arg-type]
    )

    runtime.run(AgentTask(request="Instale um pacote"))

    assert pipeline.context is runtime.context_snapshot
    assert pipeline.context is not None
    assert pipeline.context.session_id == runtime.session_id
    assert pipeline.context.project_name == "project"


def test_runtime_uses_previous_request_on_next_turn() -> None:
    pipeline = ContextAwarePipeline()
    runtime = AgentRuntime(
        execution_pipeline=pipeline,  # type: ignore[arg-type]
        context_provider=FakeContextProvider(),  # type: ignore[arg-type]
    )

    runtime.run(AgentTask(request="Primeira solicitação"))
    runtime.run(AgentTask(request="Segunda solicitação"))

    assert pipeline.context is not None
    assert pipeline.context.previous_request == "Primeira solicitação"
