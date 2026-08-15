from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.execution.controlled_executor import ControlledExecutor
from ubuntu_ai.execution.default_policy import DefaultExecutionPolicy


def test_executor_executes_complete_plan() -> None:
    plan = Plan(
        goal="Teste",
        estimated_seconds=10,
        risk=RiskLevel.LOW,
    )

    plan.add_step(
        PlanStep(
            title="echo",
            description="primeiro comando",
            command=["echo", "hello"],
        )
    )

    executor = ControlledExecutor(
        policy=DefaultExecutionPolicy(),
    )

    results = executor.execute_plan(plan)

    assert len(results) == 1
