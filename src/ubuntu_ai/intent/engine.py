from __future__ import annotations

from ubuntu_ai.intent.models import Intent
from ubuntu_ai.intent.service import IntentService


class IntentEngine:
    """Fachada pública do domínio de intenção."""

    def __init__(self, service: IntentService | None = None) -> None:
        self._service = service or IntentService()

    def interpret(self, request: str) -> Intent:
        return self._service.analyze(request)

    def history(self, limit: int = 20) -> tuple[Intent, ...]:
        return self._service.recent(limit)
