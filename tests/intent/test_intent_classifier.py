import pytest

from ubuntu_ai.intent import IntentCategory, IntentGoal, RuleBasedIntentClassifier


@pytest.mark.parametrize(
    ("user_input", "category", "goal", "confirmation"),
    [
        ("Instale Docker", IntentCategory.INSTALLATION, IntentGoal.PROVISION, True),
        ("Remova nginx", IntentCategory.MAINTENANCE, IntentGoal.REMOVE, True),
        ("Configure PostgreSQL", IntentCategory.CONFIGURATION, IntentGoal.CONFIGURE, True),
        ("Docker não funciona", IntentCategory.DIAGNOSIS, IntentGoal.REPAIR, False),
        ("Mostre o diretório atual", IntentCategory.QUERY, IntentGoal.INSPECT, False),
    ],
)
def test_classifies_common_requests(user_input, category, goal, confirmation) -> None:
    classifier = RuleBasedIntentClassifier()

    intent = classifier.classify(user_input)

    assert intent.category is category
    assert intent.goal is goal
    assert intent.requires_confirmation is confirmation


def test_unknown_request_uses_safe_fallback() -> None:
    intent = RuleBasedIntentClassifier().classify("faça algo interessante")

    assert intent.category is IntentCategory.UNKNOWN
    assert intent.goal is IntentGoal.UNKNOWN
    assert intent.confidence == 0.30


def test_rejects_empty_request() -> None:
    with pytest.raises(ValueError, match="não pode estar vazia"):
        RuleBasedIntentClassifier().classify(" ")
