from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from uuid import uuid4

from ubuntu_ai.benchmark import BenchmarkService
from ubuntu_ai.conversation.engine import ConversationEngine
from ubuntu_ai.services.ollama import OllamaService


@dataclass(frozen=True, slots=True)
class ChatResponse:
    content: str
    model: str
    route: str = "chat"
    duration: float = 0.0


class ChatService:
    """Conversa natural via Ollama sem criar ou executar planos."""

    def __init__(
        self,
        *,
        service: OllamaService,
        model: str,
        conversation_engine: ConversationEngine | None = None,
        session_id: str | None = None,
        history_limit: int = 6,
        benchmark_service: BenchmarkService | None = None,
    ) -> None:
        normalized_model = model.strip()
        if not normalized_model:
            raise ValueError("O modelo de conversa não pode estar vazio.")
        if history_limit < 1:
            raise ValueError("O limite do histórico deve ser maior que zero.")
        self._service = service
        self._model = normalized_model
        self._conversation_engine = conversation_engine
        self._session_id = session_id or f"gui-chat-{uuid4()}"
        self._history_limit = history_limit
        self._benchmark_service = benchmark_service

    def ask(self, request: str) -> ChatResponse:
        normalized = request.strip()
        if not normalized:
            raise ValueError("Digite uma pergunta.")

        history = self._history()
        prompt = self._build_prompt(normalized, history)
        started_at = perf_counter()
        try:
            content = self._service.generate(prompt=prompt, model=self._model)
        except Exception:
            if self._benchmark_service is not None:
                self._benchmark_service.record(
                    "interaction.chat",
                    perf_counter() - started_at,
                    success=False,
                )
            raise
        duration = perf_counter() - started_at
        if self._benchmark_service is not None:
            self._benchmark_service.record("interaction.chat", duration)

        if self._conversation_engine is not None:
            self._conversation_engine.remember_user(
                session_id=self._session_id,
                content=normalized,
            )
            self._conversation_engine.remember_assistant(
                session_id=self._session_id,
                content=content,
            )

        return ChatResponse(content=content, model=self._model, duration=duration)

    def _history(self) -> tuple[str, ...]:
        if self._conversation_engine is None:
            return ()
        history = self._conversation_engine.history_for_prompt(session_id=self._session_id)
        return history[-self._history_limit :]

    @staticmethod
    def _build_prompt(request: str, history: tuple[str, ...]) -> str:
        sections = [
            "Você é o Ubuntu AI Assistant, um assistente local para Linux e perguntas gerais.",
            "Responda em português do Brasil, de forma direta, correta e útil.",
            "Use no máximo seis frases, salvo quando o usuário pedir detalhes.",
            "Nesta rota você apenas conversa: não afirme que executou comandos "
            "ou alterou o sistema.",
        ]
        if history:
            sections.extend(("Histórico recente:", *history))
        sections.extend(("Pergunta do usuário:", request, "Resposta:"))
        return "\n".join(sections)
