from dataclasses import dataclass

from ubuntu_ai.agent.context import AgentContext
from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.memory.models import ExecutionRecord


@dataclass
class FakePipelineResult:
    plan: Plan
    rendered_preview: str = "preview"


class FakePipeline:
    def run(self, request: str) -> FakePipelineResult:
        return FakePipelineResult(
            plan=Plan(
                goal=request,
                estimated_seconds=1,
                risk=RiskLevel.LOW,
                steps=[
                    PlanStep(
                        title="Executar",
                        description="Executar",
                        command=["echo", "ok"],
                    )
                ],
            )
        )


class FakeContextProvider:
    def get_context(self) -> AgentContext:
        return AgentContext(
            working_directory="/tmp/project",
            operating_system="Ubuntu",
            project_name="project",
        )


class FakeControlledExecutor:
    def execute(self, request: object) -> ExecutionResult:
        command = getattr(request, "command")

        return ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Executado.",
            command=command,
            return_code=0,
            stdout="ok\n",
        )


class FakeMemoryService:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def record_execution(self, **kwargs: object) -> ExecutionRecord:
        self.calls.append(kwargs)

        result = kwargs["result"]
        assert isinstance(result, ExecutionResult)

        return ExecutionRecord.create(
            session_id=str(kwargs["session_id"]),
            user_request=str(kwargs["user_request"]),
            command=result.command or "",
            status=result.status.value,
            message=result.message,
            working_directory=str(kwargs["working_directory"]),
            project_name=str(kwargs["project_name"]),
        )


def test_runtime_persists_execution_after_confirmation() -> None:
    memory_service = FakeMemoryService()

    runtime = AgentRuntime(
        execution_pipeline=FakePipeline(),  # type: ignore[arg-type]
        context_provider=FakeContextProvider(),  # type: ignore[arg-type]
        controlled_executor=FakeControlledExecutor(),  # type: ignore[arg-type]
        memory_service=memory_service,  # type: ignore[arg-type]
    )

    runtime.run(AgentTask(request="Mostre ok"))
    runtime.confirm()

    assert len(memory_service.calls) == 1

    call = memory_service.calls[0]

    assert call["user_request"] == "Mostre ok"
    assert call["working_directory"] == "/tmp/project"
    assert call["project_name"] == "project"
