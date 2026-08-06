from ubuntu_ai.intent import (
    Intent,
    IntentCategory,
    IntentGoal,
)
from ubuntu_ai.planner.planner import Planner


def test_planner_accepts_intent_without_changing_rule_planning() -> None:
    planner = Planner()
    intent = Intent(
        request="Instale Docker",
        category=IntentCategory.INSTALLATION,
        goal=IntentGoal.PROVISION,
        confidence=0.96,
        requires_confirmation=True,
    )

    plan = planner.create_plan(intent)

    assert plan.goal == "Instalar e configurar o Docker"
    assert len(plan.steps) == 4
