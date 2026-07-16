from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.planner.rule_planner import RulePlanner


def test_rule_planner_creates_docker_plan() -> None:
    planner = RulePlanner()

    plan = planner.try_create_plan("Instale Docker")

    assert plan is not None
    assert plan.goal == "Instalar e configurar o Docker"
    assert plan.risk == RiskLevel.HIGH
    assert len(plan.steps) == 4


def test_rule_planner_returns_none_for_unknown_request() -> None:
    planner = RulePlanner()

    plan = planner.try_create_plan(
        "Configure um servidor de e-mail"
    )

    assert plan is None