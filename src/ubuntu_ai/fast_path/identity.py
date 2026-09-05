from __future__ import annotations

import re
import unicodedata


class AssistantIdentityResponder:
    """Apresenta a identidade do produto sem depender do modelo local."""

    _REQUESTS = {
        "quem e voce",
        "quem voce e",
        "o que e voce",
        "qual e o seu nome",
        "qual seu nome",
        "se apresente",
        "apresente se",
        "fale sobre voce",
    }

    _INTRODUCTION = (
        "Eu sou o Ubuntu AI Assistant, um assistente local criado para ajudar você "
        "a entender, diagnosticar e administrar computadores Ubuntu com segurança. "
        "Posso responder perguntas, consultar informações do sistema e preparar ações "
        "auditáveis. Quando uma alteração oferecer risco, mostro o plano e peço sua "
        "confirmação antes de executá-la. Recursos de IA usam o Ollama local para "
        "preservar sua privacidade.\n\n"
        "Pergunte “o que você pode fazer?” para ver minhas capacidades e exemplos."
    )

    def respond(self, request: str) -> str | None:
        if self._normalize(request) in self._REQUESTS:
            return self._INTRODUCTION
        return None

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.encode("ascii", "ignore").decode().lower()
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        return " ".join(normalized.split())
