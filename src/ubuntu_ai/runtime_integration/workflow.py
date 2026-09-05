from __future__ import annotations

from collections.abc import Callable

from ubuntu_ai.execution.models import ExecutionResult
from ubuntu_ai.learning.service import LearningService
from ubuntu_ai.memory.service import MemoryService
from ubuntu_ai.memory_intelligence.models import MemoryCandidate
from ubuntu_ai.memory_intelligence.reflection_memory import ReflectionMemoryBuilder
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
        learning_service: LearningService | None = None,
        memory_service: MemoryService | None = None,
    ) -> None:
        self._context_builder = context_builder
        self._memory_bridge = memory_bridge
        self._planner_bridge = planner_bridge
        self._execution_bridge = execution_bridge
        self._reflection_bridge = reflection_bridge
        self._learning_service = learning_service
        self._memory_service = memory_service
        self._reflection_memory_builder = ReflectionMemoryBuilder()

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
            memory=shared.memory,
        )

        if not request.execute:
            return RuntimeCycleResult(
                stage=RuntimeStage.PLANNING,
                plan=plan,
                memory=memory,
            )

        if execution_action is None:
            raise ValueError("execution_action é obrigatório quando execute=True.")

        execution = self._execution_bridge.execute(lambda: execution_action(plan))
        reflection = self._reflection_bridge.reflect(execution)

        learned_memory = self._reflection_memory_builder.build(
            report=reflection,
            project_name=(snapshot.project_name if snapshot is not None else None),
        )

        if (
            self._memory_service is not None
            and isinstance(execution, ExecutionResult)
            and execution.command is not None
        ):
            self._memory_service.record_execution(
                session_id=request.session_id,
                user_request=str(request.request),
                working_directory=(snapshot.working_directory if snapshot is not None else "."),
                project_name=(snapshot.project_name if snapshot is not None else None),
                result=execution,
            )

        if (
            self._learning_service is not None
            and isinstance(execution, ExecutionResult)
            and execution.command is not None
        ):
            project_name = snapshot.project_name if snapshot is not None else None
            self._learning_service.learn_from_execution(
                user_request=str(request.request),
                project_name=project_name,
                result=execution,
            )

        return RuntimeCycleResult(
            stage=RuntimeStage.COMPLETED,
            plan=plan,
            execution=execution,
            reflection=reflection,
            memory=memory,
            learned_memory=learned_memory,
        )
