from ubuntu_ai.agent.lifecycle import AgentLifecycle
from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime


def test_runtime_changes_lifecycle() -> None:
    runtime = AgentRuntime()

    assert runtime.lifecycle is AgentLifecycle.IDLE

    result = runtime.run(
        AgentTask(
            request="Instale Docker",
        )
    )

    assert result.success is True
    assert runtime.lifecycle is AgentLifecycle.WAITING_CONFIRMATION
