from ubuntu_ai.container.container import Container
from ubuntu_ai.intent import IntentCategory


def test_container_reuses_intent_components() -> None:
    container = Container()

    assert container.intent_repository() is container.intent_repository()
    assert container.intent_service() is container.intent_service()
    assert container.intent_engine() is container.intent_engine()


def test_container_pipeline_persists_interpreted_intent() -> None:
    container = Container()

    result = container.execution_pipeline().run("Instale Docker")
    history = container.intent_engine().history()

    assert result.intent is not None
    assert result.intent.category is IntentCategory.INSTALLATION
    assert history[-1] == result.intent
