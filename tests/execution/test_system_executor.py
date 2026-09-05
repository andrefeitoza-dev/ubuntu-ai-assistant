import shlex
from unittest.mock import Mock

import pytest

from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionStatus,
)
from ubuntu_ai.execution.system_executor import SystemExecutor
from ubuntu_ai.services.shell import CommandResult, ShellService


def test_system_executor_executes_successful_command() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.run.return_value = CommandResult(
        command="echo hello",
        return_code=0,
        stdout="hello",
        stderr="",
    )

    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(ExecutionRequest(command="echo hello"))

    assert result.status is ExecutionStatus.EXECUTED
    assert result.message == "Comando executado com sucesso."
    assert result.command == "echo hello"
    assert result.return_code == 0
    assert result.stdout == "hello"
    assert result.stderr == ""
    assert result.duration is not None
    assert result.duration >= 0

    shell_service.run.assert_called_once_with(
        ["echo", "hello"],
        timeout=30,
    )


def test_system_executor_returns_failed_result() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.run.return_value = CommandResult(
        command="false",
        return_code=1,
        stdout="",
        stderr="command failed",
    )

    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(ExecutionRequest(command="false"))

    assert result.status is ExecutionStatus.FAILED
    assert "não permitem identificar" in result.message
    assert "Próxima ação:" in result.message
    assert result.command == "false"
    assert result.return_code == 1
    assert result.stdout == ""
    assert result.stderr == "command failed"
    assert result.duration is not None
    assert result.duration >= 0


def test_system_executor_explains_permission_denied_without_elevation() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.run.return_value = CommandResult(
        command="find /protected",
        return_code=1,
        stdout="",
        stderr="find: /protected: Permission denied",
    )
    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(ExecutionRequest(command="find /protected"))

    assert result.status is ExecutionStatus.FAILED
    assert "não possui permissão" in result.message
    assert "nenhuma elevação automática" in result.message
    assert result.stderr == "find: /protected: Permission denied"


def test_system_executor_distinguishes_missing_resource() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.run.return_value = CommandResult(
        command="ls /missing",
        return_code=2,
        stdout="",
        stderr="ls: cannot access '/missing': No such file or directory",
    )
    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(ExecutionRequest(command="ls /missing"))

    assert result.status is ExecutionStatus.FAILED
    assert "não foi encontrado" in result.message
    assert "confirme o nome" in result.message


def test_system_executor_explains_permission_exception() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.run.side_effect = PermissionError(13, "Permission denied")
    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(ExecutionRequest(command="cat /protected"))

    assert result.status is ExecutionStatus.FAILED
    assert "não possui permissão" in result.message
    assert "nenhuma elevação automática" in result.message


@pytest.mark.parametrize(
    ("detail", "expected"),
    (
        ("request timed out", "tempo limite"),
        ("Temporary failure in name resolution", "resolução de nomes"),
        ("No space left on device", "espaço livre"),
        ("tool: command not found", "dependência"),
        ("invalid option -- z", "argumento incompatível"),
    ),
)
def test_system_executor_provides_actionable_failure_diagnostics(
    detail: str,
    expected: str,
) -> None:
    message = SystemExecutor._failure_message(detail)

    assert "Causa provável:" in message
    assert "Próxima ação:" in message
    assert expected in message


def test_system_executor_preserves_quoted_arguments() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.run.return_value = CommandResult(
        command="echo Olá mundo",
        return_code=0,
        stdout="Olá mundo",
        stderr="",
    )

    executor = SystemExecutor(shell_service=shell_service)

    executor.execute(ExecutionRequest(command='echo "Olá mundo"'))

    shell_service.run.assert_called_once_with(
        ["echo", "Olá mundo"],
        timeout=30,
    )


def test_system_executor_allows_long_timeout_for_graphical_apt_authentication() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.run.return_value = CommandResult(
        command="pkexec apt-get update",
        return_code=0,
        stdout="ok",
        stderr="",
    )

    SystemExecutor(shell_service=shell_service).execute(
        ExecutionRequest(command="pkexec apt-get update")
    )

    shell_service.run.assert_called_once_with(
        ["pkexec", "apt-get", "update"],
        timeout=1800,
    )


def test_system_executor_detaches_desktop_application() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.launch.return_value = CommandResult(
        command="gtk-launch firefox",
        return_code=0,
        stdout="",
        stderr="",
    )
    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(ExecutionRequest(command="gtk-launch firefox"))

    assert result.status is ExecutionStatus.EXECUTED
    assert result.message == "Solicitação de abertura enviada ao ambiente gráfico."
    shell_service.launch.assert_called_once_with(["gtk-launch", "firefox"])
    shell_service.run.assert_not_called()


def test_system_executor_detaches_xdg_open_with_quoted_path() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.launch.return_value = CommandResult(
        command="xdg-open /home/teste/Minha Pasta",
        return_code=0,
        stdout="",
        stderr="",
    )
    executor = SystemExecutor(shell_service=shell_service)

    executor.execute(ExecutionRequest(command='xdg-open "/home/teste/Minha Pasta"'))

    shell_service.launch.assert_called_once_with(["xdg-open", "/home/teste/Minha Pasta"])


def test_system_executor_does_not_run_dry_run_request() -> None:
    shell_service = Mock(spec=ShellService)
    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(
        ExecutionRequest(
            command="sudo apt update",
            dry_run=True,
        )
    )

    assert result.status is ExecutionStatus.APPROVED
    assert result.message == "Comando aprovado em modo de simulação."
    assert result.command == "sudo apt update"
    assert result.return_code is None
    assert result.stdout == ""
    assert result.stderr == ""
    assert result.duration is None

    shell_service.run.assert_not_called()


def test_system_executor_converts_shell_exception_to_failed_result() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.run.side_effect = TimeoutError("Tempo limite excedido.")

    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(ExecutionRequest(command="sleep 60"))

    assert result.status is ExecutionStatus.FAILED
    assert result.command == "sleep 60"
    assert result.return_code is None
    assert result.stdout == ""
    assert result.stderr == "Tempo limite excedido."
    assert result.duration is not None
    assert result.duration >= 0

    shell_service.run.assert_called_once_with(
        ["sleep", "60"],
        timeout=30,
    )


def test_system_executor_rejects_empty_command() -> None:
    executor = SystemExecutor()

    with pytest.raises(
        ValueError,
        match="O comando não pode estar vazio.",
    ):
        executor.execute(ExecutionRequest(command="   "))


def test_system_executor_rejects_invalid_timeout() -> None:
    with pytest.raises(
        ValueError,
        match="O timeout deve ser maior que zero.",
    ):
        SystemExecutor(timeout=0)


@pytest.mark.parametrize(
    "command",
    (
        "gtk-launch org.gnome.Calculator",
        "gtk-launch org.gnome.Terminal",
        "gtk-launch libreoffice-startcenter",
        "firefox https://github.com",
    ),
)
def test_system_executor_detaches_v22_graphical_executable(
    command: str,
) -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.launch.return_value = CommandResult(
        command=command,
        return_code=0,
        stdout="",
        stderr="",
    )
    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(ExecutionRequest(command=command))

    assert result.status is ExecutionStatus.EXECUTED
    shell_service.launch.assert_called_once_with(shlex.split(command))
    shell_service.run.assert_not_called()


def test_system_executor_does_not_report_immediate_launch_failure_as_success() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.launch.return_value = CommandResult(
        command="gtk-launch org.gnome.Calculator",
        return_code=1,
        stdout="",
        stderr="cannot open display",
    )
    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(ExecutionRequest(command="gtk-launch org.gnome.Calculator"))

    assert result.status is ExecutionStatus.FAILED
    assert result.stderr == "cannot open display"
