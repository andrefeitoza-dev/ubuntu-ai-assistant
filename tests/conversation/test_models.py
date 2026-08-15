from ubuntu_ai.conversation.models import ConversationMessage, ConversationRole


def test_create_message_normalizes_values() -> None:
    message = ConversationMessage.create(
        session_id=" session-1 ",
        role=ConversationRole.USER,
        content=" hello ",
        sequence=1,
    )

    assert message.session_id == "session-1"
    assert message.content == "hello"
    assert message.role is ConversationRole.USER


def test_create_message_rejects_invalid_sequence() -> None:
    try:
        ConversationMessage.create(
            session_id="session-1",
            role=ConversationRole.USER,
            content="hello",
            sequence=0,
        )
    except ValueError as error:
        assert "sequência" in str(error)
    else:
        raise AssertionError("ValueError esperado")
