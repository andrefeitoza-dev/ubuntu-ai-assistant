from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class ConversationRole(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True, slots=True)
class ConversationMessage:
    id: str
    session_id: str
    role: ConversationRole
    content: str
    created_at: datetime
    sequence: int

    @classmethod
    def create(
        cls,
        *,
        session_id: str,
        role: ConversationRole,
        content: str,
        sequence: int,
    ) -> "ConversationMessage":
        normalized_session = session_id.strip()
        normalized_content = content.strip()

        if not normalized_session:
            raise ValueError("O identificador da sessão não pode estar vazio.")
        if not normalized_content:
            raise ValueError("A mensagem não pode estar vazia.")
        if sequence < 1:
            raise ValueError("A sequência deve ser maior que zero.")

        return cls(
            id=str(uuid4()),
            session_id=normalized_session,
            role=role,
            content=normalized_content,
            created_at=datetime.now(UTC),
            sequence=sequence,
        )
