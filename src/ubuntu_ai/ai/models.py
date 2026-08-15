from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AIRequest:
    """Solicitação enviada para um modelo de IA."""

    prompt: str


@dataclass(slots=True, frozen=True)
class AIResponse:
    """Resposta produzida por um modelo de IA."""

    content: str
