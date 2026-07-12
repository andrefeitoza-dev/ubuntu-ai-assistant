from ubuntu_ai.services.shell import CommandResult
from ubuntu_ai.tools.shell_tool import ShellTool


class FakeShellService:
    def run(
        self,
        command: list[str],
        timeout: int = 30,
    ) -> CommandResult:
        return CommandResult(
            command=" ".join(command),
            return_code=0,
            stdout="ok",
            stderr="",
        )


def test_shell_tool_executes_command() -> None:
    tool = ShellTool(shell_service=FakeShellService())

    result = tool.execute(command=["echo", "teste"])

    assert result.success
    assert result.stdout == "ok"
    assert result.command == "echo teste"


def test_shell_tool_rejects_invalid_command() -> None:
    tool = ShellTool(shell_service=FakeShellService())

    try:
        tool.execute(command="echo teste")
    except ValueError as exc:
        assert "lista de strings" in str(exc)
    else:
        raise AssertionError("Era esperado ValueError")


def test_shell_tool_rejects_invalid_timeout() -> None:
    tool = ShellTool(shell_service=FakeShellService())

    try:
        tool.execute(command=["echo", "teste"], timeout=0)
    except ValueError as exc:
        assert "inteiro positivo" in str(exc)
    else:
        raise AssertionError("Era esperado ValueError")