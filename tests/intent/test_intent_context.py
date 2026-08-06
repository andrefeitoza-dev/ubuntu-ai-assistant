from ubuntu_ai.intent import (
    Intent,
    IntentCategory,
    IntentContextBuilder,
    IntentEntity,
    IntentGoal,
)


def test_context_builder_uses_structured_intent() -> None:
    intent = Intent(
        request="Instale Docker",
        category=IntentCategory.INSTALLATION,
        goal=IntentGoal.PROVISION,
        confidence=0.95,
        entities=(IntentEntity("Docker"),),
        requires_confirmation=True,
    )

    builder = IntentContextBuilder()

    assert builder.search_query(intent) == (
        "Instale Docker docker installation provision"
    )
    assert "Categoria: installation" in builder.prompt_context(intent)
    assert "Entidades: docker" in builder.prompt_context(intent)
