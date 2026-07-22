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

    result = executor.execute(
        ExecutionRequest(command="echo hello")
    )

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

    result = executor.execute(
        ExecutionRequest(command="false")
    )

    assert result.status is ExecutionStatus.FAILED
    assert result.message == "O comando terminou com erro."
    assert result.command == "false"
    assert result.return_code == 1
    assert result.stdout == ""
    assert result.stderr == "command failed"
    assert result.duration is not None
    assert result.duration >= 0


def test_system_executor_preserves_quoted_arguments() -> None:
    shell_service = Mock(spec=ShellService)
    shell_service.run.return_value = CommandResult(
        command="echo Olá mundo",
        return_code=0,
        stdout="Olá mundo",
        stderr="",
    )

    executor = SystemExecutor(shell_service=shell_service)

    executor.execute(
        ExecutionRequest(command='echo "Olá mundo"')
    )

    shell_service.run.assert_called_once_with(
        ["echo", "Olá mundo"],
        timeout=30,
    )


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
    shell_service.run.side_effect = TimeoutError(
        "Tempo limite excedido."
    )

    executor = SystemExecutor(shell_service=shell_service)

    result = executor.execute(
        ExecutionRequest(command="sleep 60")
    )

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
        executor.execute(
            ExecutionRequest(command="   ")
        )


def test_system_executor_rejects_invalid_timeout() -> None:
    with pytest.raises(
        ValueError,
        match="O timeout deve ser maior que zero.",
    ):
        SystemExecutor(timeout=0)