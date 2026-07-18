from ubuntu_ai.agent.engine import AgentEngine
from ubuntu_ai.agent.models import AgentTask

import pytest


def test_agent_engine_is_not_implemented() -> None:
    engine = AgentEngine()

    with pytest.raises(NotImplementedError):
        engine.run(
            AgentTask(
                request="listar arquivos",
            )
        )