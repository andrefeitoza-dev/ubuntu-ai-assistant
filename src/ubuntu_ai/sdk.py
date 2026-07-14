from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.pipeline.models import PipelineResult


class UbuntuAI:
    """API pública do Ubuntu AI Assistant para uso como SDK."""

    def __init__(
        self,
        execution_pipeline: ExecutionPipeline | None = None,
    ) -> None:
        self._execution_pipeline = (
            execution_pipeline or container.execution_pipeline()
        )

    def plan(self, request: str) -> PipelineResult:
        """Gera um plano e uma prévia segura, sem executar comandos."""

        return self._execution_pipeline.run(request)