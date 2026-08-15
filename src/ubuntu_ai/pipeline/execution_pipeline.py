from __future__ import annotations

import logging
from contextlib import AbstractContextManager, nullcontext

from ubuntu_ai.benchmark import BenchmarkService
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.executor.preview import PreviewBuilder
from ubuntu_ai.intent.engine import IntentEngine
from ubuntu_ai.intent.models import Intent
from ubuntu_ai.pipeline.models import PipelineResult
from ubuntu_ai.planner.planner import Planner
from ubuntu_ai.renderer.preview_renderer import PreviewRenderer

logger = logging.getLogger("ubuntu_ai.pipeline")


class ExecutionPipeline:
    """Orquestra intenção, planejamento, preview e renderização."""

    def __init__(
        self,
        planner: Planner | None = None,
        preview_builder: PreviewBuilder | None = None,
        preview_renderer: PreviewRenderer | None = None,
        benchmark_service: BenchmarkService | None = None,
        intent_engine: IntentEngine | None = None,
    ) -> None:
        self._planner = planner or Planner()
        self._preview_builder = preview_builder or PreviewBuilder()
        self._preview_renderer = preview_renderer or PreviewRenderer()
        self._benchmark_service = benchmark_service
        self._intent_engine = intent_engine

    def run(
        self,
        request: str | Intent,
        context: ContextSnapshot | None = None,
    ) -> PipelineResult:
        intent = self._resolve_intent(request)
        normalized_request = intent.request if intent is not None else str(request).strip()
        if not normalized_request:
            logger.warning("Pipeline recebeu uma solicitação vazia.")
            raise ValueError("A solicitação não pode estar vazia.")

        with self._measurement("pipeline"):
            plan_input: str | Intent = intent or normalized_request
            plan = self._planner.create_plan(plan_input, context=context)
            preview = self._preview_builder.build(plan)
            rendered_preview = self._preview_renderer.render(preview)
            return PipelineResult(
                plan=plan,
                preview=preview,
                rendered_preview=rendered_preview,
                intent=intent,
            )

    def _resolve_intent(self, request: str | Intent) -> Intent | None:
        if isinstance(request, Intent):
            return request
        normalized_request = request.strip()
        if not normalized_request or self._intent_engine is None:
            return None
        with self._measurement("intent"):
            return self._intent_engine.interpret(normalized_request)

    def _measurement(self, operation: str) -> AbstractContextManager[object]:
        if self._benchmark_service is None:
            return nullcontext()
        return self._benchmark_service.measure(operation)
