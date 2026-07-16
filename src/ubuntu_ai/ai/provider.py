from abc import ABC, abstractmethod

from ubuntu_ai.ai.models import AIRequest, AIResponse


class AIProvider(ABC):
    """Contrato para provedores de inteligência artificial."""

    @abstractmethod
    def generate(self, request: AIRequest) -> AIResponse:
        """Gera uma resposta para a solicitação recebida."""