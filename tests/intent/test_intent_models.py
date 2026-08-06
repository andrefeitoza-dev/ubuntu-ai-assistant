import pytest

from ubuntu_ai.intent import Intent, IntentCategory, IntentEntity, IntentGoal


def test_intent_normalizes_request_and_entities() -> None:
    intent = Intent(
        request="  instalar Docker  ",
        category=IntentCategory.INSTALLATION,
        goal=IntentGoal.PROVISION,
        confidence=0.9,
        entities=(IntentEntity(" Docker "),),
    )

    assert intent.request == "instalar Docker"
    assert intent.entity_names == ("docker",)


def test_intent_rejects_invalid_confidence() -> None:
    with pytest.raises(ValueError, match="confiança"):
        Intent(
            request="teste",
            category=IntentCategory.UNKNOWN,
            goal=IntentGoal.UNKNOWN,
            confidence=1.1,
        )


def test_entity_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="nome"):
        IntentEntity(" ")
