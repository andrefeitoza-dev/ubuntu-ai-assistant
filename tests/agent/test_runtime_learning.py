from dataclasses import dataclass

from ubuntu_ai.agent.context import AgentContext
from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus


@dataclass
class FakePipelineResult:
    plan: Plan
    rendered_preview: str = "preview"


class FakePipeline:
    def run(self, request: str) -> FakePipelineResult:
        return FakePipelineResult(
            Plan(
                goal=request,
                estimated_seconds=1,
                risk=RiskLevel.LOW,
                steps=[PlanStep("Executar", "Executar", ["echo", "ok"])],
            )
        )


class FakeContextProvider:
    def get_context(self) -> AgentContext:
        return AgentContext("/tmp/project", "Ubuntu", "project")


class FakeExecutor:
    def execute(self, request: object) -> ExecutionResult:
        return ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="ok",
            command=getattr(request, "command"),
            return_code=0,
        )


class FakeLearningService:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def learn_from_execution(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return object()


def test_runtime_updates_learning_after_execution() -> None:
    learning = FakeLearningService()
    runtime = AgentRuntime(
        execution_pipeline=FakePipeline(),  # type: ignore[arg-type]
        context_provider=FakeContextProvider(),  # type: ignore[arg-type]
        controlled_executor=FakeExecutor(),  # type: ignore[arg-type]
        learning_service=learning,  # type: ignore[arg-type]
    )

    runtime.run(AgentTask(request="Mostre ok"))
    runtime.confirm()

    assert len(learning.calls) == 1
    assert learning.calls[0]["user_request"] == "Mostre ok"
    assert learning.calls[0]["project_name"] == "project"
