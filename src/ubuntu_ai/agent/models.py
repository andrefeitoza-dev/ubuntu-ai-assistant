from dataclasses import dataclass, field

from ubuntu_ai.pipeline.models import PipelineResult


@dataclass(slots=True, frozen=True)
class AgentTask:
    """Representa uma solicitação recebida pelo Agent Runtime."""

    request: str


@dataclass(slots=True, frozen=True)
class AgentResult:
    """Resultado produzido pelo Agent Runtime."""

    success: bool
    message: str
    pipeline_result: PipelineResult | None = None


@dataclass(slots=True)
class AgentSession:
    """Representa uma sessão ativa do agente."""

    history: list[str] = field(default_factory=list)

    def remember(self, message: str) -> None:
        """Adiciona uma mensagem ao histórico da sessão."""

        self.history.append(message)

    def clear(self) -> None:
        """Limpa todo o histórico da sessão."""

        self.history.clear()
