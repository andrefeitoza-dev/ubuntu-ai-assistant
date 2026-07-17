from ubuntu_ai.agent.context import AgentContext, ContextProvider
from ubuntu_ai.agent.models import AgentResult, AgentTask
from ubuntu_ai.agent.session import SessionManager
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline


class AgentRuntime:
    """Orquestra contexto, sessão e pipeline de execução do agente."""

    def __init__(
        self,
        execution_pipeline: ExecutionPipeline | None = None,
        session_manager: SessionManager | None = None,
        context_provider: ContextProvider | None = None,
    ) -> None:
        self._execution_pipeline = execution_pipeline or ExecutionPipeline()
        self._session_manager = session_manager or SessionManager()
        self._context_provider = context_provider or ContextProvider()

    @property
    def session_manager(self) -> SessionManager:
        """Retorna o gerenciador de sessão utilizado pelo runtime."""
        return self._session_manager

    def get_context(self) -> AgentContext:
        """Obtém o contexto atual do ambiente."""
        return self._context_provider.get_context()

    def run(self, task: AgentTask) -> AgentResult:
        """Processa uma tarefa por meio do pipeline de planejamento."""

        request = task.request.strip()

        if not request:
            raise ValueError("A solicitação não pode estar vazia.")

        context = self.get_context()

        self._session_manager.remember(f"Usuário: {request}")
        self._session_manager.remember(
            self._format_context_message(context),
        )

        pipeline_result = self._execution_pipeline.run(request)
        message = pipeline_result.rendered_preview

        self._session_manager.remember(f"Agente: {message}")

        return AgentResult(
            success=True,
            message=message,
            pipeline_result=pipeline_result,
        )

    @staticmethod
    def _format_context_message(context: AgentContext) -> str:
        """Formata o contexto detectado para registro na sessão."""

        project_description = (
            context.project_name
            if context.project_name is not None
            else "nenhum projeto detectado"
        )

        return (
            f"Contexto: diretório={context.working_directory}; "
            f"projeto={project_description}; "
            f"sistema={context.operating_system}"
        )