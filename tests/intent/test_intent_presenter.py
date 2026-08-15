from ubuntu_ai.intent.models import (
    Intent,
    IntentCategory,
    IntentEntity,
    IntentGoal,
)
from ubuntu_ai.intent.presenter import IntentPresenter


def test_presenter_formats_intent_for_interfaces() -> None:
    intent = Intent(
        request="Instale Docker",
        category=IntentCategory.INSTALLATION,
        goal=IntentGoal.PROVISION,
        confidence=0.97,
        entities=(IntentEntity("Docker"),),
        requires_confirmation=True,
    )

    view = IntentPresenter().present(intent)

    assert view.category == "installation"
    assert view.goal == "provision"
    assert view.confidence_percent == "97%"
    assert view.entities == "docker"
    assert view.requires_confirmation == "sim"
