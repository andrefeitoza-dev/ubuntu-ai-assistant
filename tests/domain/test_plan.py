from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel


def test_add_step() -> None:
    plan = Plan(
        goal="Instalar Docker",
        estimated_seconds=120,
        risk=RiskLevel.LOW,
    )

    plan.add_step(
        PlanStep(
            title="Atualizar repositórios",
            description="Executa apt update",
            command=["sudo", "apt", "update"],
        )
    )

    assert len(plan.steps) == 1
    assert plan.steps[0].command == ["sudo", "apt", "update"]
