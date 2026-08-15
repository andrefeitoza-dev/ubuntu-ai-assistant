from __future__ import annotations

from typing import Protocol

from ubuntu_ai.conversation.models import ConversationMessage


class ConversationRepository(Protocol):
    def save_message(self, message: ConversationMessage) -> None:
        """Persiste uma mensagem de conversa."""

    def list_messages(
        self,
        *,
        session_id: str,
        limit: int = 50,
    ) -> tuple[ConversationMessage, ...]:
        """Retorna mensagens em ordem cronológica."""

    def next_sequence(self, *, session_id: str) -> int:
        """Retorna a próxima sequência disponível para a sessão."""

    def clear_session(self, *, session_id: str) -> None:
        """Remove as mensagens persistidas da sessão."""
