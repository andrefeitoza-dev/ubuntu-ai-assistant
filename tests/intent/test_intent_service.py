from ubuntu_ai.intent import (
    InMemoryIntentRepository,
    IntentCategory,
    IntentEngine,
    IntentService,
)


def test_service_persists_analyzed_intent() -> None:
    repository = InMemoryIntentRepository()
    service = IntentService(repository=repository)

    created = service.analyze("Instale Docker")

    assert service.recent() == (created,)


def test_repository_returns_most_recent_first() -> None:
    repository = InMemoryIntentRepository()
    service = IntentService(repository=repository)
    first = service.analyze("Mostre o diretório atual")
    second = service.analyze("Instale Docker")

    assert service.recent(limit=2) == (second, first)


def test_engine_exposes_public_facade() -> None:
    engine = IntentEngine()

    intent = engine.interpret("Docker não funciona")

    assert intent.category is IntentCategory.DIAGNOSIS
