from ubuntu_ai.agents.memory_agent import MemoryAgent, MemoryAgentPayload
from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.memory_intelligence.models import (
    MemoryCandidate,
    MemoryKind,
    MemoryQuery,
)


def test_memory_agent_selects_memories() -> None:
    result = MemoryAgent().handle(
        AgentTask(
            kind=AgentKind.MEMORY,
            payload=MemoryAgentPayload(
                query=MemoryQuery(text="uv", limit=1),
                candidates=(
                    MemoryCandidate(
                        kind=MemoryKind.PROJECT,
                        content="package_manager=uv",
                        similarity=0.9,
                    ),
                ),
            ),
        )
    )

    assert len(result.output.items) == 1
