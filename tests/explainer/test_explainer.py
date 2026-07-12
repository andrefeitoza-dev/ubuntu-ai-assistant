from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.explainer.explainer import Explainer


def test_explainer_returns_text() -> None:
    plan = Plan(
        goal="Instalar Docker",
        estimated_seconds=120,
        risk=RiskLevel.HIGH,
    )

    plan.add_step(
        PlanStep(
            title="Atualizar repositórios",
            description="Atualiza os índices de pacotes do Ubuntu.",
            command=["sudo", "apt", "update"],
        )
    )

    text = Explainer().explain(plan)

    assert "Instalar Docker" in text
    assert "Atualizar repositórios" in text
    assert "sudo apt update" in text
    assert "Risco: HIGH" in text
