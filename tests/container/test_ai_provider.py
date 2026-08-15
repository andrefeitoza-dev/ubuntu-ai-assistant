from ubuntu_ai.ai.models import AIRequest, AIResponse
from ubuntu_ai.ai.ollama_provider import OllamaProvider
from ubuntu_ai.ai.provider import AIProvider
from ubuntu_ai.container import Container


class FakeProvider(AIProvider):
    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(content=request.prompt)


def test_ollama_provider_is_singleton() -> None:
    container = Container()

    first = container.ollama_provider()
    second = container.ollama_provider()

    assert isinstance(first, OllamaProvider)
    assert first is second


def test_ai_provider_returns_configured_provider() -> None:
    container = Container()

    assert container.ai_provider() is container.ollama_provider()


def test_container_can_register_and_select_custom_provider() -> None:
    container = Container()
    provider = FakeProvider()

    container.register_ai_provider("custom", provider, select=True)

    assert container.config().ai_provider == "custom"
    assert container.ai_provider() is provider


def test_container_reset_discards_cached_dependencies() -> None:
    container = Container()
    first_config = container.config()
    first_provider = container.ai_provider()

    container.reset()

    assert container.config() is not first_config
    assert container.ai_provider() is not first_provider
