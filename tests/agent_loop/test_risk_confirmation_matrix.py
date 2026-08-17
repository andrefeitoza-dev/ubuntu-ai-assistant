from __future__ import annotations

from dataclasses import dataclass

import pytest

from ubuntu_ai.agent.models import AgentResult, AgentTask
from ubuntu_ai.agent_loop import AgentLoopController, LoopState, StopReason
from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.executor.preview import ExecutionPreview
from ubuntu_ai.pipeline.models import PipelineResult


@dataclass
class RiskRuntime:
    risk: RiskLevel
    confirm_calls: int = 0

    def run(self, task: AgentTask) -> AgentResult:
        plan = Plan(
            goal=task.request,
            steps=(),
            risk=self.risk,
        )
        return AgentResult(
            success=True,
            message="Plano criado para validação.",
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

    def confirm(self) -> tuple[ExecutionResult, ...]:
        self.confirm_calls += 1
        return (
            ExecutionResult(
                status=ExecutionStatus.EXECUTED,
                message="Execução simulada.",
                command="simulated-command",
                return_code=0,
            ),
        )


@pytest.mark.parametrize(
    ("risk", "auto_executes"),
    (
        (RiskLevel.LOW, True),
        (RiskLevel.MEDIUM, False),
        (RiskLevel.HIGH, False),
        (RiskLevel.CRITICAL, False),
    ),
)
def test_only_low_risk_auto_executes(
    risk: RiskLevel,
    auto_executes: bool,
) -> None:
    runtime = RiskRuntime(risk)
    controller = AgentLoopController(runtime=runtime)  # type: ignore[arg-type]

    snapshot = controller.start(f"validar risco {risk.value}")

    if auto_executes:
        assert snapshot.state is LoopState.COMPLETED
        assert snapshot.stop_reason is StopReason.GOAL_REACHED
        assert snapshot.requires_confirmation is False
        assert runtime.confirm_calls == 1
        assert len(snapshot.records) == 1
        return

    assert snapshot.state is LoopState.WAITING_CONFIRMATION
    assert snapshot.requires_confirmation is True
    assert runtime.confirm_calls == 0
    assert snapshot.records == ()


@pytest.mark.parametrize(
    "risk",
    (
        RiskLevel.MEDIUM,
        RiskLevel.HIGH,
        RiskLevel.CRITICAL,
    ),
)
def test_sensitive_risks_execute_only_after_confirmation(
    risk: RiskLevel,
) -> None:
    runtime = RiskRuntime(risk)
    controller = AgentLoopController(runtime=runtime)  # type: ignore[arg-type]

    waiting = controller.start(f"validar confirmação {risk.value}")

    assert waiting.state is LoopState.WAITING_CONFIRMATION
    assert runtime.confirm_calls == 0

    completed = controller.confirm()

    assert completed.state is LoopState.COMPLETED
    assert completed.stop_reason is StopReason.GOAL_REACHED
    assert runtime.confirm_calls == 1
    assert len(completed.records) == 1


@pytest.mark.parametrize(
    "risk",
    (
        RiskLevel.HIGH,
        RiskLevel.CRITICAL,
    ),
)
def test_cancelling_sensitive_plan_never_executes(
    risk: RiskLevel,
) -> None:
    runtime = RiskRuntime(risk)
    controller = AgentLoopController(runtime=runtime)  # type: ignore[arg-type]

    controller.start(f"cancelar risco {risk.value}")
    cancelled = controller.cancel()

    assert cancelled.state is LoopState.CANCELLED
    assert cancelled.stop_reason is StopReason.USER_CANCELLED
    assert runtime.confirm_calls == 0
    assert cancelled.records == ()
