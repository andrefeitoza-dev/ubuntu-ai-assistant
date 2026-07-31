from ubuntu_ai.ai.models import AIRequest, AIResponse
from ubuntu_ai.ai.provider import AIProvider
from ubuntu_ai.services.ollama import OllamaService


class OllamaProvider(AIProvider):
    """Implementação de AIProvider utilizando o Ollama local."""

    def __init__(
        self,
        service: OllamaService,
        model: str,
    ) -> None:
        self._service = service
        self._model = model

    def generate(self, request: AIRequest) -> AIResponse:
        """Gera uma resposta usando o modelo configurado."""

        content = self._service.generate(
            prompt=request.prompt,
            model=self._model,
        )

        return AIResponse(content=content)
    
    