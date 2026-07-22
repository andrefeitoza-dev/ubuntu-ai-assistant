from shlex import join

from ubuntu_ai.agent.context import AgentContext, ContextProvider
from ubuntu_ai.agent.lifecycle import AgentLifecycle
from ubuntu_ai.agent.models import AgentResult, AgentTask
from ubuntu_ai.agent.session import SessionManager
from ubuntu_ai.confirmation.engine import ConfirmationEngine
from ubuntu_ai.confirmation.models import Confirmation
from ubuntu_ai.execution.controlled_executor import ControlledExecutor
from ubuntu_ai.execution.default_policy import DefaultExecutionPolicy
from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.pipeline.models import PipelineResult


class AgentRuntime:
    """Orquestra contexto, sessão, planejamento e autorização do agente."""

    def __init__(
        self,
        execution_pipeline: ExecutionPipeline | None = None,
        session_manager: SessionManager | None = None,
        context_provider: ContextProvider | None = None,
        confirmation_engine: ConfirmationEngine | None = None,
        controlled_executor: ControlledExecutor | None = None,
    ) -> None:
        self._execution_pipeline = execution_pipeline or ExecutionPipeline()
        self._session_manager = session_manager or SessionManager()
        self._context_provider = context_provider or ContextProvider()
        self._confirmation_engine = confirmation_engine or ConfirmationEngine()
        self._controlled_executor = controlled_executor or ControlledExecutor(
            DefaultExecutionPolicy()
        )

        self._confirmation: Confirmation | None = None
        self._pipeline_result: PipelineResult | None = None
        self._lifecycle = AgentLifecycle.IDLE

    @property
    def session_manager(self) -> SessionManager:
        """Retorna o gerenciador de sessão utilizado pelo runtime."""

        return self._session_manager

    @property
    def lifecycle(self) -> AgentLifecycle:
        """Retorna o estado atual do runtime."""

        return self._lifecycle

    def get_context(self) -> AgentContext:
        """Obtém o contexto atual do ambiente."""

        return self._context_provider.get_context()

    def run(self, task: AgentTask) -> AgentResult:
        """Processa uma tarefa por meio do pipeline de planejamento."""

        request = task.request.strip()

        if not request:
            raise ValueError("A solicitação não pode estar vazia.")

        self._lifecycle = AgentLifecycle.PLANNING

        context = self.get_context()

        self._session_manager.remember(f"Usuário: {request}")
        self._session_manager.remember(
            self._format_context_message(context),
        )

        pipeline_result = self._execution_pipeline.run(request)
        self._pipeline_result = pipeline_result

        message = pipeline_result.rendered_preview

        self._session_manager.remember(f"Agente: {message}")

        self._confirmation = self._confirmation_engine.create()
        self._lifecycle = AgentLifecycle.WAITING_CONFIRMATION

        return AgentResult(
            success=True,
            message=message,
            pipeline_result=pipeline_result,
        )

    def confirm(self) -> tuple[ExecutionResult, ...]:
        """Confirma e avalia os comandos do plano pendente."""

        if self._confirmation is None:
            raise RuntimeError("Não existe confirmação pendente.")

        if self._pipeline_result is None:
            raise RuntimeError("Não existe plano pendente para execução.")

        self._confirmation_engine.confirm(self._confirmation)
        self._lifecycle = AgentLifecycle.EXECUTING

        results: list[ExecutionResult] = []

        for step in self._pipeline_result.plan.steps:
            command = join(step.command)

            result = self._controlled_executor.execute(
                ExecutionRequest(command=command)
            )

            results.append(result)
            self._remember_execution_result(command, result)

            if result.status is ExecutionStatus.BLOCKED:
                break

        self._confirmation = None
        self._lifecycle = AgentLifecycle.COMPLETED

        return tuple(results)

    def _remember_execution_result(
        self,
        command: str,
        result: ExecutionResult,
    ) -> None:
        """Registra o resultado da autorização no histórico da sessão."""

        status_description = {
            ExecutionStatus.APPROVED: "aprovada",
            ExecutionStatus.BLOCKED: "bloqueada",
            ExecutionStatus.EXECUTED: "executada",
            ExecutionStatus.FAILED: "falhou",
        }[result.status]

        self._session_manager.remember(
            f"Execução {status_description}: {command} — {result.message}"
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