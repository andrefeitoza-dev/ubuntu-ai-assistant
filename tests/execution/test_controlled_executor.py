from unittest.mock import Mock

from ubuntu_ai.execution.controlled_executor import ControlledExecutor
from ubuntu_ai.execution.default_policy import DefaultExecutionPolicy
from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)
from ubuntu_ai.execution.system_executor import SystemExecutor


def test_executor_approves_safe_command_without_system_executor() -> None:
    executor = ControlledExecutor(DefaultExecutionPolicy())

    result = executor.execute(
        ExecutionRequest(command="pwd")
    )

    assert result.status is ExecutionStatus.APPROVED
    assert result.message == "Comando autorizado."
    assert result.command == "pwd"


def test_executor_blocks_rm() -> None:
    executor = ControlledExecutor(DefaultExecutionPolicy())

    result = executor.execute(
        ExecutionRequest(command="rm -rf /")
    )

    assert result.status is ExecutionStatus.BLOCKED
    assert "bloqueado" in result.message
    assert result.command == "rm -rf /"


def test_executor_blocks_empty_command() -> None:
    executor = ControlledExecutor(DefaultExecutionPolicy())

    result = executor.execute(
        ExecutionRequest(command="")
    )

    assert result.status is ExecutionStatus.BLOCKED
    assert result.command == ""


def test_executor_delegates_authorized_command_to_system_executor() -> None:
    system_executor = Mock(spec=SystemExecutor)
    system_executor.execute.return_value = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        message="Comando executado com sucesso.",
        command="pwd",
        return_code=0,
        stdout="/home/user/project",
    )

    executor = ControlledExecutor(
        policy=DefaultExecutionPolicy(),
        system_executor=system_executor,
    )

    request = ExecutionRequest(command="pwd")
    result = executor.execute(request)

    assert result.status is ExecutionStatus.EXECUTED
    assert result.command == "pwd"
    assert result.return_code == 0
    assert result.stdout == "/home/user/project"

    system_executor.execute.assert_called_once_with(request)


def test_executor_does_not_delegate_blocked_command() -> None:
    system_executor = Mock(spec=SystemExecutor)

    executor = ControlledExecutor(
        policy=DefaultExecutionPolicy(),
        system_executor=system_executor,
    )

    result = executor.execute(
        ExecutionRequest(command="rm -rf /")
    )

    assert result.status is ExecutionStatus.BLOCKED
    assert result.command == "rm -rf /"

    system_executor.execute.assert_not_called()