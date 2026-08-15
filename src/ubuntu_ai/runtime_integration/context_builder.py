from __future__ import annotations

from ubuntu_ai.context.engine import ContextEngine
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.runtime_integration.models import RuntimeRequest


class RuntimeContextBuilder:
    """Resolve contexto explícito ou cria um snapshot pelo ContextEngine."""

    def __init__(self, context_engine: ContextEngine | None = None) -> None:
        self._context_engine = context_engine

    def build(self, request: RuntimeRequest) -> ContextSnapshot | None:
        if isinstance(request.context, ContextSnapshot):
            return request.context

        if self._context_engine is None:
            return None

        return self._context_engine.build(session_id=request.session_id)
