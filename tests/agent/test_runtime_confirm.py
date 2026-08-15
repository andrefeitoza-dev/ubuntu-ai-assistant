from unittest.mock import Mock

from ubuntu_ai.agent.lifecycle import AgentLifecycle
from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.execution.controlled_executor import ControlledExecutor
from ubuntu_ai.execution.models import (
    ExecutionResult,
    ExecutionStatus,
)


def test_runtime_confirms_pending_execution() -> None:
    fake_executor = Mock(spec=ControlledExecutor)

    fake_executor.execute.return_value = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        message="Executado.",
        command="sudo apt update",
    )

    runtime = AgentRuntime(
        controlled_executor=fake_executor,
    )

    runtime.run(
        AgentTask(
            request="Instale Docker",
        )
    )

    runtime.confirm()

    assert runtime.lifecycle is AgentLifecycle.COMPLETED
