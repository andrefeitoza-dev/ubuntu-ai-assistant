from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.intent import Intent, IntentCategory, IntentGoal
from ubuntu_ai.reflection import ReflectionEngine


def test_reflection_warns_about_unknown_intent() -> None:
    intent = Intent(
        request="faça uma coisa",
        category=IntentCategory.UNKNOWN,
        goal=IntentGoal.UNKNOWN,
        confidence=0.3,
    )

    report = ReflectionEngine().before_execution(
        Plan("Objetivo", 30, RiskLevel.LOW),
        intent=intent,
    )

    codes = {finding.code for finding in report.findings}
    assert "unknown-intent" in codes
    assert "low-intent-confidence" in codes
