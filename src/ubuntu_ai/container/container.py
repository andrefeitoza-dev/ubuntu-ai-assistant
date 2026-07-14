from ubuntu_ai.executor.preview import PreviewBuilder
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.planner.planner import Planner
from ubuntu_ai.renderer.preview_renderer import PreviewRenderer


class Container:
    """Container simples para gerenciamento de dependências."""

    def __init__(self) -> None:
        self._singletons: dict[str, object] = {}

    def _singleton(self, key: str, factory):
        """Obtém ou cria um singleton."""

        if key not in self._singletons:
            self._singletons[key] = factory()

        return self._singletons[key]

    def planner(self) -> Planner:
        return Planner()

    def preview_builder(self) -> PreviewBuilder:
        return PreviewBuilder()

    def preview_renderer(self) -> PreviewRenderer:
        return PreviewRenderer()

    def execution_pipeline(self) -> ExecutionPipeline:
        return ExecutionPipeline(
            planner=self.planner(),
            preview_builder=self.preview_builder(),
            preview_renderer=self.preview_renderer(),
        )