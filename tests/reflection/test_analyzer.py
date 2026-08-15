from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.reflection import ReflectionAnalyzer, ReflectionSeverity


def test_plan_reflection_detects_duplicate_commands() -> None:
    plan = Plan("Atualizar", 10, RiskLevel.MEDIUM)
    for title in ("A", "B"):
        plan.add_step(PlanStep(title, title, ["apt", "update"], "apt"))

    report = ReflectionAnalyzer().analyze_plan(plan)

    assert any(item.code == "duplicate-command" for item in report.findings)
    assert report.approved is True


def test_plan_reflection_blocks_destructive_low_risk_plan() -> None:
    plan = Plan("Apagar", 5, RiskLevel.LOW)
    plan.add_step(PlanStep("Apagar", "Apaga dados", ["rm", "-rf", "/tmp/x"], "shell"))

    report = ReflectionAnalyzer().analyze_plan(plan)

    assert report.approved is False
    assert any(item.severity is ReflectionSeverity.CRITICAL for item in report.findings)


def test_execution_reflection_diagnoses_missing_command() -> None:
    result = ExecutionResult(
        status=ExecutionStatus.FAILED,
        message="falhou",
        command="missing-tool",
        return_code=127,
        stderr="command not found",
    )

    report = ReflectionAnalyzer().analyze_execution(command="missing-tool", result=result)

    assert report.approved is False
    assert any(item.code == "command-unavailable" for item in report.findings)
