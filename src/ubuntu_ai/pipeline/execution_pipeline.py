from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.executor.preview import PreviewBuilder
from ubuntu_ai.pipeline.models import PipelineResult
from ubuntu_ai.planner.planner import Planner
from ubuntu_ai.renderer.preview_renderer import PreviewRenderer


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
            raise ValueError("A solicitação não pode estar vazia.")

        plan = self._planner.create_plan(normalized_request, context=context)
        preview = self._preview_builder.build(plan)
        rendered_preview = self._preview_renderer.render(preview)

        return PipelineResult(
            plan=plan,
            preview=preview,
            rendered_preview=rendered_preview,
        )