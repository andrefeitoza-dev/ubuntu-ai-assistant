from unittest.mock import Mock, call

from ubuntu_ai.agent.lifecycle import AgentLifecycle
from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.execution.controlled_executor import ControlledExecutor
from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)


def test_runtime_executes_all_steps_after_confirmation() -> None:
    controlled_executor = Mock(spec=ControlledExecutor)
    controlled_executor.execute.return_value = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        message="Comando executado com sucesso.",
        return_code=0,
    )

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
    assert len(results) == 4
    assert all(
        result.status is ExecutionStatus.EXECUTED
        for result in results
    )
    assert controlled_executor.execute.call_count == 4


def test_runtime_sends_plan_commands_to_controlled_executor() -> None:
    controlled_executor = Mock(spec=ControlledExecutor)
    controlled_executor.execute.return_value = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        message="Comando executado com sucesso.",
        return_code=0,
    )

    runtime = AgentRuntime(
        controlled_executor=controlled_executor,
    )

    runtime.run(
        AgentTask(
            request="Instale Docker",
        )
    )

    runtime.confirm()

    assert controlled_executor.execute.call_args_list[:2] == [
        call(ExecutionRequest(command="sudo apt update")),
        call(
            ExecutionRequest(
                command="sudo apt install -y docker.io"
            )
        ),
    ]


def test_runtime_stops_after_blocked_command() -> None:
    controlled_executor = Mock(spec=ControlledExecutor)
    controlled_executor.execute.side_effect = [
        ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Comando executado com sucesso.",
            command="sudo apt update",
            return_code=0,
        ),
        ExecutionResult(
            status=ExecutionStatus.BLOCKED,
            message="Comando bloqueado pela política de segurança.",
            command="sudo apt install -y docker.io",
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

    assert results[0].status is ExecutionStatus.EXECUTED
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


def test_runtime_returns_failed_execution_result() -> None:
    controlled_executor = Mock(spec=ControlledExecutor)
    controlled_executor.execute.side_effect = [
        ExecutionResult(
            status=ExecutionStatus.FAILED,
            message="O comando terminou com erro.",
            command="sudo apt update",
            return_code=1,
            stderr="Falha ao atualizar os repositórios.",
        ),
        ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Comando executado com sucesso.",
            return_code=0,
        ),
        ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Comando executado com sucesso.",
            return_code=0,
        ),
        ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Comando executado com sucesso.",
            return_code=0,
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
    assert len(results) == 4
    assert results[0].status is ExecutionStatus.FAILED
    assert results[0].return_code == 1
    assert results[0].stderr == "Falha ao atualizar os repositórios."


def test_runtime_records_execution_results_in_session() -> None:
    controlled_executor = Mock(spec=ControlledExecutor)
    controlled_executor.execute.side_effect = [
        ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Comando executado com sucesso.",
            command="sudo apt update",
            return_code=0,
        ),
        ExecutionResult(
            status=ExecutionStatus.BLOCKED,
            message="Comando bloqueado pela política de segurança.",
            command="sudo apt install -y docker.io",
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
        "Execução executada: sudo apt update" in message
        for message in history
    )
    assert any(
        "Execução bloqueada: sudo apt install -y docker.io" in message
        for message in history
    )


def test_runtime_records_failed_execution_in_session() -> None:
    controlled_executor = Mock(spec=ControlledExecutor)
    controlled_executor.execute.side_effect = [
        ExecutionResult(
            status=ExecutionStatus.FAILED,
            message="O comando terminou com erro.",
            command="sudo apt update",
            return_code=1,
        ),
        ExecutionResult(
            status=ExecutionStatus.BLOCKED,
            message="Execução interrompida.",
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
        "Execução falhou: sudo apt update" in message
        for message in history
    )