from ubuntu_ai.container.container import Container
from ubuntu_ai.tui.app import TerminalApp


def test_container_builds_terminal_app() -> None:
    assert isinstance(Container().terminal_app(), TerminalApp)
