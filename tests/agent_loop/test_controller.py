from dataclasses import dataclass

from ubuntu_ai.agent.models import AgentResult, AgentTask
from ubuntu_ai.agent_loop import (
    AgentLoopConfig,
    AgentLoopController,
    LoopState,
    StopReason,
)
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus


@dataclass
class FakeRuntime:
    batches: list[tuple[ExecutionResult, ...]]

    def __post_init__(self) -> None:
        self.requests: list[str] = []

    def run(self, task: AgentTask) -> AgentResult:
        self.requests.append(task.request)
        return AgentResult(success=True, message=f"plan: {task.request}")

    def confirm(self) -> tuple[ExecutionResult, ...]:
        return self.batches.pop(0)


def result(status: ExecutionStatus, message: str = "ok") -> ExecutionResult:
    return ExecutionResult(status=status, message=message, command="cmd")


def test_successful_loop_requires_confirmation_and_completes() -> None:
    runtime = FakeRuntime([ (result(ExecutionStatus.EXECUTED),) ])
    controller = AgentLoopController(runtime=runtime)  # type: ignore[arg-type]

    planned = controller.start("configurar serviço")
    assert planned.state is LoopState.WAITING_CONFIRMATION
    assert planned.requires_confirmation

    completed = controller.confirm()
    assert completed.state is LoopState.COMPLETED
    assert completed.stop_reason is StopReason.GOAL_REACHED
    assert len(completed.records) == 1


def test_failure_replans_and_requires_new_confirmation() -> None:
    runtime = FakeRuntime(
        [
            (result(ExecutionStatus.FAILED, "first failed"),),
            (result(ExecutionStatus.EXECUTED),),
        ]
    )
    controller = AgentLoopController(runtime=runtime)  # type: ignore[arg-type]

    controller.start("instalar pacote")
    replanned = controller.confirm()

    assert replanned.state is LoopState.WAITING_CONFIRMATION
    assert replanned.iteration == 2
    assert "Objetivo original: instalar pacote" in runtime.requests[1]

    completed = controller.confirm()
    assert completed.state is LoopState.COMPLETED
    assert len(completed.records) == 2


def test_blocked_execution_stops_without_replanning() -> None:
    runtime = FakeRuntime([ (result(ExecutionStatus.BLOCKED),) ])
    controller = AgentLoopController(runtime=runtime)  # type: ignore[arg-type]

    controller.start("ação perigosa")
    snapshot = controller.confirm()

    assert snapshot.state is LoopState.BLOCKED
    assert snapshot.stop_reason is StopReason.EXECUTION_BLOCKED
    assert len(runtime.requests) == 1


def test_loop_stops_at_iteration_limit() -> None:
    runtime = FakeRuntime(
        [
            (result(ExecutionStatus.FAILED, "failure one"),),
            (result(ExecutionStatus.FAILED, "failure two"),),
        ]
    )
    controller = AgentLoopController(
        runtime=runtime,  # type: ignore[arg-type]
        config=AgentLoopConfig(max_iterations=2, max_stalled_iterations=3),
    )

    controller.start("resolver problema")
    controller.confirm()
    snapshot = controller.confirm()

    assert snapshot.state is LoopState.FAILED
    assert snapshot.stop_reason is StopReason.MAX_ITERATIONS


def test_cancel_pending_plan() -> None:
    runtime = FakeRuntime([ (result(ExecutionStatus.EXECUTED),) ])
    controller = AgentLoopController(runtime=runtime)  # type: ignore[arg-type]

    controller.start("configurar")
    snapshot = controller.cancel()

    assert snapshot.state is LoopState.CANCELLED
    assert snapshot.stop_reason is StopReason.USER_CANCELLED
