import pytest

from ubuntu_ai.ai import AIRequest, AIResponse, OllamaProvider


class FakeOllamaService:
    def __init__(self) -> None:
        self.prompt: str | None = None
        self.model: str | None = None

    def generate(self, prompt: str, model: str) -> str:
        self.prompt = prompt
        self.model = model

        return "Resposta produzida pelo Ollama."


class FailingOllamaService:
    def generate(self, prompt: str, model: str) -> str:
        raise RuntimeError("Falha ao gerar resposta com o Ollama.")


def test_ollama_provider_generates_ai_response() -> None:
    service = FakeOllamaService()
    provider = OllamaProvider(
        service=service,
        model="qwen2.5:3b",
    )

    response = provider.generate(
        AIRequest(prompt="Explique Docker"),
    )

    assert isinstance(response, AIResponse)
    assert response.content == "Resposta produzida pelo Ollama."


def test_ollama_provider_uses_configured_model() -> None:
    service = FakeOllamaService()
    provider = OllamaProvider(
        service=service,
        model="qwen2.5:3b",
    )

    provider.generate(AIRequest(prompt="Explique Docker"))

    assert service.prompt == "Explique Docker"
    assert service.model == "qwen2.5:3b"


def test_ollama_provider_propagates_service_error() -> None:
    provider = OllamaProvider(
        service=FailingOllamaService(),
        model="qwen2.5:3b",
    )

    with pytest.raises(
        RuntimeError,
        match="Falha ao gerar resposta com o Ollama",
    ):
        provider.generate(AIRequest(prompt="Explique Docker"))