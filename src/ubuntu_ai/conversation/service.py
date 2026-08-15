from __future__ import annotations

from ubuntu_ai.conversation.models import ConversationMessage, ConversationRole
from ubuntu_ai.conversation.repository import ConversationRepository


class ConversationService:
    """Serviço de aplicação para histórico conversacional persistente."""

    def __init__(
        self,
        repository: ConversationRepository,
        *,
        history_limit: int = 12,
        character_limit: int = 6000,
    ) -> None:
        if history_limit < 1:
            raise ValueError("O limite do histórico deve ser maior que zero.")
        if character_limit < 1:
            raise ValueError("O limite de caracteres deve ser maior que zero.")
        self._repository = repository
        self._history_limit = history_limit
        self._character_limit = character_limit

    def add_message(
        self,
        *,
        session_id: str,
        role: ConversationRole,
        content: str,
    ) -> ConversationMessage:
        message = ConversationMessage.create(
            session_id=session_id,
            role=role,
            content=content,
            sequence=self._repository.next_sequence(session_id=session_id),
        )
        self._repository.save_message(message)
        return message

    def history(self, *, session_id: str) -> tuple[ConversationMessage, ...]:
        return self._repository.list_messages(
            session_id=session_id,
            limit=self._history_limit,
        )

    def prompt_history(self, *, session_id: str) -> tuple[str, ...]:
        messages = self.history(session_id=session_id)
        rendered = [f"{message.role.value}: {message.content}" for message in messages]

        selected: list[str] = []
        used = 0
        for line in reversed(rendered):
            size = len(line)
            if selected and used + size > self._character_limit:
                break
            selected.append(line)
            used += size

        return tuple(reversed(selected))

    def clear(self, *, session_id: str) -> None:
        self._repository.clear_session(session_id=session_id)
