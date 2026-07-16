from ubuntu_ai.ai.ollama_provider import OllamaProvider
from ubuntu_ai.container import Container


def test_ollama_provider_is_singleton() -> None:
    container = Container()

    first = container.ollama_provider()
    second = container.ollama_provider()

    assert isinstance(first, OllamaProvider)
    assert first is second


def test_ai_provider_returns_configured_provider() -> None:
    container = Container()

    assert container.ai_provider() is container.ollama_provider()