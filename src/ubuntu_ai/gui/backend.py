from __future__ import annotations

from ubuntu_ai.agent_loop.models import LoopSnapshot
from ubuntu_ai.container.bootstrap import container


class GUIBackend:
    """Adapta o ApplicationRuntime para a interface gráfica."""

    def __init__(self) -> None:
        self._runtime = container.application_runtime()

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
