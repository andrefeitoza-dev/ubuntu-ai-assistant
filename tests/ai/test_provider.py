from ubuntu_ai.ai import AIProvider, AIRequest, AIResponse


class FakeAIProvider(AIProvider):
    """Provedor falso usado apenas nos testes."""

    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(content=f"Resposta para: {request.prompt}")


def test_ai_provider_generates_response() -> None:
    provider = FakeAIProvider()
    request = AIRequest(prompt="Explique Docker")

    response = provider.generate(request)

    assert isinstance(response, AIResponse)
    assert response.content == "Resposta para: Explique Docker"


def test_ai_request_preserves_prompt() -> None:
    request = AIRequest(prompt="Instale Docker")

    assert request.prompt == "Instale Docker"


def test_ai_response_preserves_content() -> None:
    response = AIResponse(content="Docker é uma plataforma de containers.")

    assert response.content == "Docker é uma plataforma de containers."