from __future__ import annotations

from collections.abc import Callable

from ubuntu_ai.memory_intelligence.models import MemoryCandidate
from ubuntu_ai.runtime_integration.context_builder import RuntimeContextBuilder
from ubuntu_ai.runtime_integration.execution_bridge import RuntimeExecutionBridge
from ubuntu_ai.runtime_integration.memory_bridge import RuntimeMemoryBridge
from ubuntu_ai.runtime_integration.models import (
    RuntimeCycleResult,
    RuntimeRequest,
    RuntimeStage,
)
from ubuntu_ai.runtime_integration.planner_bridge import RuntimePlannerBridge
from ubuntu_ai.runtime_integration.reflection_bridge import RuntimeReflectionBridge
from ubuntu_ai.runtime_integration.shared_context import SharedAgentContext


class RuntimeWorkflow:
    """Orquestra um ciclo completo do runtime multiagente."""

    def __init__(
        self,
        *,
        context_builder: RuntimeContextBuilder,
        memory_bridge: RuntimeMemoryBridge,
        planner_bridge: RuntimePlannerBridge,
        execution_bridge: RuntimeExecutionBridge,
        reflection_bridge: RuntimeReflectionBridge,
    ) -> None:
        self._context_builder = context_builder
        self._memory_bridge = memory_bridge
        self._planner_bridge = planner_bridge
        self._execution_bridge = execution_bridge
        self._reflection_bridge = reflection_bridge

    def run(
        self,
        request: RuntimeRequest,
        *,
        execution_action: Callable[[object], object] | None = None,
    ) -> RuntimeCycleResult:
        snapshot = self._context_builder.build(request)
        shared = SharedAgentContext(snapshot=snapshot)

        candidates = tuple(
            candidate
            for candidate in request.memory_candidates
            if isinstance(candidate, MemoryCandidate)
        )

        memory = self._memory_bridge.select(
            request_text=str(request.request),
            context=snapshot,
            candidates=candidates,
        )
        shared = shared.with_memory(memory)

        plan = self._planner_bridge.create_plan(
            request=request.request,
            context=shared.snapshot,
        )

        if not request.execute:
            return RuntimeCycleResult(
                stage=RuntimeStage.PLANNING,
                plan=plan,
                memory=memory,
            )

        if execution_action is None:
            raise ValueError(
                "execution_action é obrigatório quando execute=True."
            )

        execution = self._execution_bridge.execute(
            lambda: execution_action(plan)
        )
        reflection = self._reflection_bridge.reflect(execution)

        return RuntimeCycleResult(
            stage=RuntimeStage.COMPLETED,
            plan=plan,
            execution=execution,
            reflection=reflection,
            memory=memory,
        )
