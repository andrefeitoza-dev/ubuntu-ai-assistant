from ubuntu_ai.agents.execution_agent import (
    ExecutionAgent,
    ExecutionAgentPayload,
)
from ubuntu_ai.agents.models import AgentKind, AgentTask


def test_execution_agent_runs_callable() -> None:
    result = ExecutionAgent().handle(
        AgentTask(
            kind=AgentKind.EXECUTION,
            payload=ExecutionAgentPayload(
                action=lambda: "executed",
            ),
        )
    )

    assert result.output == "executed"
