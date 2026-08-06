from __future__ import annotations

import logging
from contextlib import AbstractContextManager, nullcontext

from ubuntu_ai.benchmark import BenchmarkService
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.executor.preview import PreviewBuilder
from ubuntu_ai.pipeline.models import PipelineResult
from ubuntu_ai.planner.planner import Planner
from ubuntu_ai.renderer.preview_renderer import PreviewRenderer

logger = logging.getLogger("ubuntu_ai.pipeline")


class ExecutionPipeline:
    """Orquestra planejamento, preview e renderização."""

    def __init__(
        self,
        planner: Planner | None = None,
        preview_builder: PreviewBuilder | None = None,
        preview_renderer: PreviewRenderer | None = None,
        benchmark_service: BenchmarkService | None = None,
    ) -> None:
        self._planner = planner or Planner()
        self._preview_builder = preview_builder or PreviewBuilder()
        self._preview_renderer = preview_renderer or PreviewRenderer()
        self._benchmark_service = benchmark_service

    def run(self, request: str, context: ContextSnapshot | None = None) -> PipelineResult:
        normalized_request = request.strip()
        if not normalized_request:
            logger.warning("Pipeline recebeu uma solicitação vazia.")
            raise ValueError("A solicitação não pode estar vazia.")
        with self._measurement("pipeline"):
            plan = self._planner.create_plan(normalized_request, context=context)
            preview = self._preview_builder.build(plan)
            rendered_preview = self._preview_renderer.render(preview)
            return PipelineResult(plan=plan, preview=preview, rendered_preview=rendered_preview)

    def _measurement(self, operation: str) -> AbstractContextManager[object]:
        if self._benchmark_service is None:
            return nullcontext()
        return self._benchmark_service.measure(operation)
