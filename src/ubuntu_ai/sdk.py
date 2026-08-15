from ubuntu_ai.agent.models import AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.pipeline.models import PipelineResult


class UbuntuAI:
    """API pública do Ubuntu AI Assistant para uso como SDK."""

    def __init__(
        self,
        agent_runtime: AgentRuntime | None = None,
        execution_pipeline: ExecutionPipeline | None = None,
    ) -> None:
        if agent_runtime is not None and execution_pipeline is not None:
            raise ValueError(
                "Informe agent_runtime ou execution_pipeline, não ambos.",
            )

        if agent_runtime is not None:
            self._agent_runtime = agent_runtime
        elif execution_pipeline is not None:
            self._agent_runtime = AgentRuntime(
                execution_pipeline=execution_pipeline,
            )
        else:
            self._agent_runtime = container.agent_runtime()

    def plan(self, request: str) -> PipelineResult:
        """Gera um plano e uma prévia segura, sem executar comandos."""

        agent_result = self._agent_runtime.run(
            AgentTask(request=request),
        )

        if agent_result.pipeline_result is None:
            raise RuntimeError(
                "O Agent Runtime não retornou um resultado de planejamento.",
            )

        return agent_result.pipeline_result
