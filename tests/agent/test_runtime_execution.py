from unittest.mock import Mock

from ubuntu_ai.agent.lifecycle import AgentLifecycle
from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.execution.controlled_executor import ControlledExecutor
from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)


def test_runtime_evaluates_all_steps_after_confirmation() -> None:
    runtime = AgentRuntime()

    runtime.run(
        AgentTask(
            request="Instale Docker",
        )
    )

    results = runtime.confirm()

    assert runtime.lifecycle is AgentLifecycle.COMPLETED
    assert len(results) == 4
    assert all(
        result.status is ExecutionStatus.APPROVED
        for result in results
    )


def test_runtime_stops_after_blocked_command() -> None:
    controlled_executor = Mock(spec=ControlledExecutor)
    controlled_executor.execute.side_effect = [
        ExecutionResult(
            status=ExecutionStatus.APPROVED,
            message="Comando autorizado.",
        ),
        ExecutionResult(
            status=ExecutionStatus.BLOCKED,
            message="Comando bloqueado pela política de segurança.",
        ),
    ]

    runtime = AgentRuntime(
        controlled_executor=controlled_executor,
    )

    runtime.run(
        AgentTask(
            request="Instale Docker",
        )
    )

    results = runtime.confirm()

    assert runtime.lifecycle is AgentLifecycle.COMPLETED
    assert len(results) == 2

    assert results[0].status is ExecutionStatus.APPROVED
    assert results[1].status is ExecutionStatus.BLOCKED

    assert controlled_executor.execute.call_count == 2

    controlled_executor.execute.assert_any_call(
        ExecutionRequest(command="sudo apt update")
    )
    controlled_executor.execute.assert_any_call(
        ExecutionRequest(
            command="sudo apt install -y docker.io"
        )
    )


def test_runtime_records_execution_results_in_session() -> None:
    controlled_executor = Mock(spec=ControlledExecutor)
    controlled_executor.execute.side_effect = [
        ExecutionResult(
            status=ExecutionStatus.APPROVED,
            message="Comando autorizado.",
        ),
        ExecutionResult(
            status=ExecutionStatus.BLOCKED,
            message="Comando bloqueado pela política de segurança.",
        ),
    ]

    runtime = AgentRuntime(
        controlled_executor=controlled_executor,
    )

    runtime.run(
        AgentTask(
            request="Instale Docker",
        )
    )

    runtime.confirm()

    history = runtime.session_manager.session.history

    assert any(
        "Execução aprovada: sudo apt update" in message
        for message in history
    )
    assert any(
        "Execução bloqueada: sudo apt install -y docker.io" in message
        for message in history
    )