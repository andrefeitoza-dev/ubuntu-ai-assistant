from ubuntu_ai.agent.lifecycle import AgentLifecycle
from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime


def test_runtime_confirms_pending_execution() -> None:
    runtime = AgentRuntime()

    runtime.run(
        AgentTask(
            request="Instale Docker",
        )
    )

    runtime.confirm()

    assert runtime.lifecycle is AgentLifecycle.COMPLETED