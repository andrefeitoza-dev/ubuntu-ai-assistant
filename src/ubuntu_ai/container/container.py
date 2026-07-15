from collections.abc import Callable
from typing import TypeVar, cast

from ubuntu_ai.core.config import AppConfig
from ubuntu_ai.executor.preview import PreviewBuilder
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.planner.planner import Planner
from ubuntu_ai.renderer.preview_renderer import PreviewRenderer
from ubuntu_ai.services.ollama import OllamaService

T = TypeVar("T")


class Container:
    """Container simples para gerenciamento de dependências."""

    def __init__(self) -> None:
        self._singletons: dict[str, object] = {}

    def _singleton(
        self,
        key: str,
        factory: Callable[[], T],
    ) -> T:
        """Obtém ou cria um singleton."""

        if key not in self._singletons:
            self._singletons[key] = factory()

        return cast(T, self._singletons[key])

    def config(self) -> AppConfig:
        """Retorna a configuração única da aplicação."""

        return self._singleton("config", AppConfig)

    def ollama_service(self) -> OllamaService:
        """Retorna o cliente único do Ollama."""

        config = self.config()

        return self._singleton(
            "ollama_service",
            lambda: OllamaService(
                base_url=config.ollama_base_url,
                timeout=config.request_timeout,
            ),
        )

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