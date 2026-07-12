from ubuntu_ai.domain.plan import Plan, PlanStep, RiskLevel
from ubuntu_ai.executor.executor import Executor


def test_executor_returns_execution_steps() -> None:
    plan = Plan(
        goal="Teste",
        risk=RiskLevel.LOW,
        estimated_seconds=5,
        steps=[
            PlanStep(
                title="Primeira etapa",
                description="Descrição",
                command="echo teste",
            )
        ],
    )

    executor = Executor()

    result = executor.execute(plan)

    assert len(result) == 1
    assert result[0] == "Executando: Primeira etapa"