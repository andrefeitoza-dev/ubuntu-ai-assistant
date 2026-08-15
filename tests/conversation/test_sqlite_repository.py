from pathlib import Path

from ubuntu_ai.conversation.models import ConversationMessage, ConversationRole
from ubuntu_ai.conversation.sqlite_repository import SQLiteConversationRepository


def test_repository_persists_and_orders_messages(tmp_path: Path) -> None:
    repository = SQLiteConversationRepository(tmp_path / "memory.db")

    second = ConversationMessage.create(
        session_id="session-1",
        role=ConversationRole.ASSISTANT,
        content="second",
        sequence=2,
    )
    first = ConversationMessage.create(
        session_id="session-1",
        role=ConversationRole.USER,
        content="first",
        sequence=1,
    )
    repository.save_message(second)
    repository.save_message(first)

    messages = repository.list_messages(session_id="session-1")

    assert [message.content for message in messages] == ["first", "second"]
    assert repository.next_sequence(session_id="session-1") == 3


def test_repository_isolates_and_clears_sessions(tmp_path: Path) -> None:
    repository = SQLiteConversationRepository(tmp_path / "memory.db")
    for session_id in ("one", "two"):
        repository.save_message(
            ConversationMessage.create(
                session_id=session_id,
                role=ConversationRole.USER,
                content=session_id,
                sequence=1,
            )
        )

    repository.clear_session(session_id="one")

    assert repository.list_messages(session_id="one") == ()
    assert len(repository.list_messages(session_id="two")) == 1
