from pathlib import Path

from ubuntu_ai.conversation.models import ConversationRole
from ubuntu_ai.conversation.service import ConversationService
from ubuntu_ai.conversation.sqlite_repository import SQLiteConversationRepository


def test_service_builds_prompt_history(tmp_path: Path) -> None:
    service = ConversationService(
        SQLiteConversationRepository(tmp_path / "memory.db"),
        history_limit=3,
    )
    service.add_message(
        session_id="session",
        role=ConversationRole.USER,
        content="install docker",
    )
    service.add_message(
        session_id="session",
        role=ConversationRole.ASSISTANT,
        content="plan created",
    )

    assert service.prompt_history(session_id="session") == (
        "user: install docker",
        "assistant: plan created",
    )


def test_service_applies_character_limit(tmp_path: Path) -> None:
    service = ConversationService(
        SQLiteConversationRepository(tmp_path / "memory.db"),
        character_limit=20,
    )
    service.add_message(
        session_id="session",
        role=ConversationRole.USER,
        content="old message that is long",
    )
    service.add_message(
        session_id="session",
        role=ConversationRole.USER,
        content="new",
    )

    assert service.prompt_history(session_id="session") == ("user: new",)
