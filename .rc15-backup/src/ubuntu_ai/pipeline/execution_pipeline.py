from __future__ import annotations

import logging

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
    ) -> None:
        self._planner = planner or Planner()
        self._preview_builder = preview_builder or PreviewBuilder()
        self._preview_renderer = preview_renderer or PreviewRenderer()

    def run(
        self,
        request: str,
        context: ContextSnapshot | None = None,
    ) -> PipelineResult:
        """Processa uma solicitação sem executar alterações no sistema."""

        normalized_request = request.strip()

        if not normalized_request:
            logger.warning(
                "Pipeline recebeu uma solicitação vazia."
            )
            raise ValueError("A solicitação não pode estar vazia.")

        logger.info(
            "Pipeline iniciado.",
            extra={
                "request": normalized_request,
            },
        )

        plan = self._planner.create_plan(
            normalized_request,
            context=context,
        )

        logger.info(
            "Planejamento concluído.",
            extra={
                "steps": len(plan.steps),
                "risk": plan.risk.value,
            },
        )

        preview = self._preview_builder.build(plan)

        logger.info(
            "Preview criado.",
            extra={
                "steps": len(preview.steps),
            },
        )

        rendered_preview = self._preview_renderer.render(preview)

        logger.info("Pipeline finalizado com sucesso.")

        return PipelineResult(
            plan=plan,
            preview=preview,
            rendered_preview=rendered_preview,
        )