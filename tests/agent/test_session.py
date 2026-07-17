from ubuntu_ai.agent.session import SessionManager


def test_session_manager_starts_with_empty_history() -> None:
    manager = SessionManager()

    assert manager.session.history == []


def test_session_manager_remembers_messages() -> None:
    manager = SessionManager()

    manager.remember("Mensagem de teste")

    assert manager.session.history == ["Mensagem de teste"]


def test_session_manager_resets_session_history() -> None:
    manager = SessionManager()

    manager.remember("Mensagem de teste")
    manager.reset()

    assert manager.session.history == []