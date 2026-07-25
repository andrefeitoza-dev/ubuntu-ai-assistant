from __future__ import annotations

from ubuntu_ai.conversation.models import ConversationRole
from ubuntu_ai.conversation.service import ConversationService


class ConversationEngine:
    """Fachada de alto nível para registrar e recuperar conversas."""

    def __init__(self, service: ConversationService) -> None:
        self._service = service

    def remember_user(self, *, session_id: str, content: str) -> None:
        self._service.add_message(
            session_id=session_id,
            role=ConversationRole.USER,
            content=content,
        )

    def remember_assistant(self, *, session_id: str, content: str) -> None:
        self._service.add_message(
            session_id=session_id,
            role=ConversationRole.ASSISTANT,
            content=content,
        )

    def history_for_prompt(self, *, session_id: str) -> tuple[str, ...]:
        return self._service.prompt_history(session_id=session_id)

    def clear(self, *, session_id: str) -> None:
        self._service.clear(session_id=session_id)
