from ubuntu_ai.execution.controlled_executor import ControlledExecutor
from ubuntu_ai.execution.default_policy import DefaultExecutionPolicy
from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionStatus,
)


def test_executor_approves_safe_command() -> None:
    executor = ControlledExecutor(DefaultExecutionPolicy())

    result = executor.execute(
        ExecutionRequest(command="pwd")
    )

    assert result.status is ExecutionStatus.APPROVED
    assert result.message == "Comando autorizado."


def test_executor_blocks_rm() -> None:
    executor = ControlledExecutor(DefaultExecutionPolicy())

    result = executor.execute(
        ExecutionRequest(command="rm -rf /")
    )

    assert result.status is ExecutionStatus.BLOCKED
    assert "bloqueado" in result.message


def test_executor_blocks_empty_command() -> None:
    executor = ControlledExecutor(DefaultExecutionPolicy())

    result = executor.execute(
        ExecutionRequest(command="")
    )

    assert result.status is ExecutionStatus.BLOCKED