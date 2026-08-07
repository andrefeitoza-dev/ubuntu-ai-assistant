from __future__ import annotations

from ubuntu_ai.agents.factory import build_default_agent_coordinator
from ubuntu_ai.context.engine import ContextEngine
from ubuntu_ai.planner.planner import Planner
from ubuntu_ai.runtime_integration.context_builder import RuntimeContextBuilder
from ubuntu_ai.runtime_integration.execution_bridge import RuntimeExecutionBridge
from ubuntu_ai.runtime_integration.memory_bridge import RuntimeMemoryBridge
from ubuntu_ai.runtime_integration.planner_bridge import RuntimePlannerBridge
from ubuntu_ai.runtime_integration.reflection_bridge import RuntimeReflectionBridge
from ubuntu_ai.runtime_integration.runtime import MultiAgentRuntime
from ubuntu_ai.runtime_integration.workflow import RuntimeWorkflow


def build_multi_agent_runtime(
    *,
    planner: Planner,
    context_engine: ContextEngine | None = None,
) -> MultiAgentRuntime:
    """Compõe o runtime multiagente sobre componentes existentes."""

    coordinator = build_default_agent_coordinator(planner=planner)

    workflow = RuntimeWorkflow(
        context_builder=RuntimeContextBuilder(context_engine),
        memory_bridge=RuntimeMemoryBridge(coordinator),
        planner_bridge=RuntimePlannerBridge(coordinator),
        execution_bridge=RuntimeExecutionBridge(coordinator),
        reflection_bridge=RuntimeReflectionBridge(coordinator),
    )

    return MultiAgentRuntime(workflow)
