from ubuntu_ai.tui.theme import ConsoleTheme


def test_console_theme_has_default_tokens() -> None:
    theme = ConsoleTheme()

    assert theme.success == "green"
    assert theme.error == "red"
