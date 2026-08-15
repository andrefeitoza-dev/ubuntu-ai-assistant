from ubuntu_ai.renderer.command_formatter import CommandFormatter


def test_formatter_joins_command_arguments() -> None:
    formatter = CommandFormatter()

    result = formatter.format(["sudo", "apt", "update"])

    assert result == "sudo apt update"


def test_formatter_quotes_arguments_with_spaces() -> None:
    formatter = CommandFormatter()

    result = formatter.format(["echo", "Olá Ubuntu"])

    assert result == "echo 'Olá Ubuntu'"


def test_formatter_preserves_string_command() -> None:
    formatter = CommandFormatter()

    result = formatter.format("docker --version")

    assert result == "docker --version"
