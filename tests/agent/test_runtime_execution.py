from ubuntu_ai.agent.lifecycle import AgentLifecycle
from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.execution.models import ExecutionStatus


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