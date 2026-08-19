from __future__ import annotations

from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.agents.execution_agent import ExecutionAgent
from ubuntu_ai.agents.memory_agent import MemoryAgent
from ubuntu_ai.agents.planner_agent import PlannerAgent
from ubuntu_ai.agents.reflection_agent import ReflectionAgent
from ubuntu_ai.agents.registry import AgentRegistry
from ubuntu_ai.agents.specialists import (
    NetworkAgent,
    ServicesAgent,
    StorageAgent,
    SystemAgent,
)
from ubuntu_ai.planner.planner import Planner


def build_default_agent_coordinator(
    *,
    planner: Planner,
) -> AgentCoordinator:
    """Compõe o conjunto padrão de agentes sem depender do Container."""

    registry = AgentRegistry()
    registry.register(PlannerAgent(planner))
    registry.register(ExecutionAgent())
    registry.register(MemoryAgent())
    registry.register(ReflectionAgent())
    registry.register(SystemAgent())
    registry.register(NetworkAgent())
    registry.register(StorageAgent())
    registry.register(ServicesAgent())

    return AgentCoordinator(registry)
