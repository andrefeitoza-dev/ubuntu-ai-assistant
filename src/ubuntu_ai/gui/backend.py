from __future__ import annotations

from ubuntu_ai.agent_loop.models import LoopSnapshot
from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.interaction import ChatResponse, InteractionDecision


class GUIBackend:
    """Adapta o ApplicationRuntime para a interface gráfica."""

    def __init__(self) -> None:
        self._runtime = container.application_runtime()
        self._router = container.interaction_router()
        self._chat = container.chat_service()

    def route(self, request: str) -> InteractionDecision:
        """Classifica a solicitação antes de acionar qualquer executor."""

        return self._router.route(request)

    def chat(self, request: str) -> ChatResponse:
        """Responde sem criar plano nem executar comandos."""

        return self._chat.ask(request)

    def start(self, request: str) -> LoopSnapshot:
        request = request.strip()

        if not request:
            raise ValueError("Digite uma solicitação.")

        return self._runtime.start(request)

    def confirm(self) -> LoopSnapshot:
        """Confirma explicitamente o plano atualmente pendente."""
        return self._runtime.confirm()

    def cancel(self) -> LoopSnapshot:
        """Cancela o plano atualmente pendente."""
        return self._runtime.cancel()

    def snapshot(self) -> LoopSnapshot:
        return self._runtime.snapshot()
