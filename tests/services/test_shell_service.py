from ubuntu_ai.services.shell import ShellService


def test_shell_echo() -> None:
    shell = ShellService()

    result = shell.run(["echo", "Ubuntu AI"])

    assert result.success
    assert result.stdout == "Ubuntu AI"
