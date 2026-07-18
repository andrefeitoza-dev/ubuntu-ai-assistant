from ubuntu_ai.agent.engine import AgentEngine
from ubuntu_ai.agent.models import AgentTask


def test_agent_engine_delegates_to_runtime() -> None:
    engine = AgentEngine()

    result = engine.run(
        AgentTask(
            request="Instale Docker",
        )
    )

    assert result.success is True
    assert result.pipeline_result is not None