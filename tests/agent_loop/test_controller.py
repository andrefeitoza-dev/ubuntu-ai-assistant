from dataclasses import dataclass

from ubuntu_ai.agent.models import AgentResult, AgentTask
from ubuntu_ai.agent_loop import (
    AgentLoopConfig,
    AgentLoopController,
    LoopState,
    StopReason,
)
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.executor.preview import ExecutionPreview


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
    runtime = FakeRuntime([(result(ExecutionStatus.EXECUTED),)])
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
    runtime = FakeRuntime([(result(ExecutionStatus.BLOCKED),)])
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
    runtime = FakeRuntime([(result(ExecutionStatus.EXECUTED),)])
    controller = AgentLoopController(runtime=runtime)  # type: ignore[arg-type]

    controller.start("configurar")
    snapshot = controller.cancel()

    assert snapshot.state is LoopState.CANCELLED
    assert snapshot.stop_reason is StopReason.USER_CANCELLED


def test_low_risk_plan_executes_without_human_confirmation() -> None:
    from ubuntu_ai.agent.models import AgentResult
    from ubuntu_ai.domain.plan import Plan
    from ubuntu_ai.domain.risk import RiskLevel
    from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
    from ubuntu_ai.pipeline.models import PipelineResult

    class LowRiskRuntime:
        def __init__(self) -> None:
            self.confirm_calls = 0

        def run(self, task):
            plan = Plan(
                goal="Consultar disco",
                steps=(),
                risk=RiskLevel.LOW,
            )
            return AgentResult(
                success=True,
                message="Plano criado.",
                pipeline_result=PipelineResult(
                    plan=plan,
                    preview=ExecutionPreview(
                        goal=plan.goal,
                        risk=plan.risk,
                        estimated_seconds=plan.estimated_seconds,
                        steps=(),
                    ),
                    rendered_preview="",
                ),
            )

        def confirm(self):
            self.confirm_calls += 1
            return (
                ExecutionResult(
                    status=ExecutionStatus.EXECUTED,
                    message="Executado.",
                    command="df -h",
                    return_code=0,
                ),
            )

    runtime = LowRiskRuntime()

    controller = AgentLoopController(
        runtime=runtime,
    )

    snapshot = controller.start("verifique o disco")

    assert snapshot.state is LoopState.COMPLETED
    assert not snapshot.requires_confirmation
    assert runtime.confirm_calls == 1
    assert len(snapshot.records) == 1


def test_high_risk_plan_still_requires_confirmation() -> None:
    from ubuntu_ai.agent.models import AgentResult
    from ubuntu_ai.domain.plan import Plan
    from ubuntu_ai.domain.risk import RiskLevel
    from ubuntu_ai.pipeline.models import PipelineResult

    class HighRiskRuntime:
        def __init__(self) -> None:
            self.confirm_calls = 0

        def run(self, task):
            plan = Plan(
                goal="Alterar sistema",
                steps=(),
                risk=RiskLevel.HIGH,
            )
            return AgentResult(
                success=True,
                message="Plano criado.",
                pipeline_result=PipelineResult(
                    plan=plan,
                    preview=ExecutionPreview(
                        goal=plan.goal,
                        risk=plan.risk,
                        estimated_seconds=plan.estimated_seconds,
                        steps=(),
                    ),
                    rendered_preview="",
                ),
            )

        def confirm(self):
            self.confirm_calls += 1
            return ()

    runtime = HighRiskRuntime()

    controller = AgentLoopController(
        runtime=runtime,
    )

    snapshot = controller.start("altere o sistema")

    assert snapshot.state is LoopState.WAITING_CONFIRMATION
    assert snapshot.requires_confirmation
    assert runtime.confirm_calls == 0


def test_cancelled_planning_cannot_overwrite_a_new_cycle() -> None:
    import threading

    class DelayedRuntime:
        def __init__(self) -> None:
            self.started = threading.Event()
            self.release = threading.Event()

        def run(self, task: AgentTask) -> AgentResult:
            if task.request == "solicitação antiga":
                self.started.set()
                self.release.wait(timeout=2)
            return AgentResult(success=True, message=f"plan: {task.request}")

        def confirm(self) -> tuple[ExecutionResult, ...]:
            return ()

    runtime = DelayedRuntime()
    controller = AgentLoopController(runtime=runtime)  # type: ignore[arg-type]

    old_thread = threading.Thread(
        target=controller.start,
        args=("solicitação antiga",),
    )
    old_thread.start()
    assert runtime.started.wait(timeout=1)

    cancelled = controller.cancel()
    assert cancelled.state is LoopState.CANCELLED

    current = controller.start("solicitação nova")
    assert current.state is LoopState.WAITING_CONFIRMATION
    assert current.pending_plan is not None
    assert current.pending_plan.message == "plan: solicitação nova"

    runtime.release.set()
    old_thread.join(timeout=1)

    final = controller.snapshot()
    assert final.state is LoopState.WAITING_CONFIRMATION
    assert final.pending_plan is not None
    assert final.pending_plan.message == "plan: solicitação nova"
