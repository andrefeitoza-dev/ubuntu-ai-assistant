from inspect import signature
from shlex import join
from uuid import uuid4

from ubuntu_ai.agent.context import AgentContext, ContextProvider
from ubuntu_ai.agent.lifecycle import AgentLifecycle
from ubuntu_ai.agent.models import AgentResult, AgentTask
from ubuntu_ai.agent.session import SessionManager
from ubuntu_ai.confirmation.engine import ConfirmationEngine
from ubuntu_ai.confirmation.models import Confirmation
from ubuntu_ai.context.engine import ContextEngine
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.execution.controlled_executor import ControlledExecutor
from ubuntu_ai.execution.default_policy import DefaultExecutionPolicy
from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)
from ubuntu_ai.execution.system_executor import SystemExecutor
from ubuntu_ai.memory.service import MemoryService
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.pipeline.models import PipelineResult


class AgentRuntime:
    """Orquestra planejamento, confirmação e execução do agente."""

    def __init__(
        self,
        execution_pipeline: ExecutionPipeline | None = None,
        session_manager: SessionManager | None = None,
        context_provider: ContextProvider | None = None,
        confirmation_engine: ConfirmationEngine | None = None,
        controlled_executor: ControlledExecutor | None = None,
        memory_service: MemoryService | None = None,
        context_engine: ContextEngine | None = None,
    ) -> None:
        self._execution_pipeline = execution_pipeline or ExecutionPipeline()
        self._session_manager = session_manager or SessionManager()
        self._context_provider = context_provider or ContextProvider()
        self._confirmation_engine = confirmation_engine or ConfirmationEngine()
        self._controlled_executor = controlled_executor or ControlledExecutor(
            policy=DefaultExecutionPolicy(),
            system_executor=SystemExecutor(),
        )
        self._memory_service = memory_service
        self._context_engine = context_engine or ContextEngine(
            context_provider=self._context_provider,
            session_manager=self._session_manager,
            memory_service=self._memory_service,
        )

        self._confirmation: Confirmation | None = None
        self._pipeline_result: PipelineResult | None = None
        self._pending_request: str | None = None
        self._pending_context: AgentContext | None = None
        self._context_snapshot: ContextSnapshot | None = None
        self._session_id = str(uuid4())
        self._lifecycle = AgentLifecycle.IDLE

    @property
    def session_manager(self) -> SessionManager:
        """Retorna o gerenciador de sessão utilizado pelo runtime."""

        return self._session_manager

    @property
    def lifecycle(self) -> AgentLifecycle:
        """Retorna o estado atual do runtime."""

        return self._lifecycle

    @property
    def session_id(self) -> str:
        """Retorna o identificador da sessão atual."""

        return self._session_id

    @property
    def context_snapshot(self) -> ContextSnapshot | None:
        """Retorna o snapshot contextual mais recente."""

        return self._context_snapshot

    def get_context(self) -> AgentContext:
        """Obtém o contexto atual do ambiente."""

        return self._context_provider.get_context()

    def run(self, task: AgentTask) -> AgentResult:
        """Processa uma tarefa por meio do pipeline de planejamento."""

        request = task.request.strip()

        if not request:
            raise ValueError("A solicitação não pode estar vazia.")

        self._lifecycle = AgentLifecycle.PLANNING

        context_snapshot = self._context_engine.build(session_id=self._session_id)
        context = AgentContext(
            working_directory=context_snapshot.working_directory,
            operating_system=context_snapshot.operating_system,
            project_name=context_snapshot.project_name,
        )
        self._context_snapshot = context_snapshot
        self._pending_request = request
        self._pending_context = context

        self._session_manager.remember(f"Usuário: {request}")
        self._session_manager.remember(
            self._format_context_message(context)
        )

        pipeline_result = self._run_pipeline(request, context_snapshot)
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
        """Confirma e executa os comandos autorizados do plano pendente."""

        if self._confirmation is None:
            raise RuntimeError("Não existe confirmação pendente.")

        if self._pipeline_result is None:
            raise RuntimeError("Não existe plano pendente para execução.")

        if not self._pipeline_result.plan.steps:
            raise RuntimeError(
                "O plano não possui etapas executáveis."
            )

        self._confirmation_engine.confirm(self._confirmation)
        self._lifecycle = AgentLifecycle.EXECUTING

        results: list[ExecutionResult] = []

        for step in self._pipeline_result.plan.steps:
            command = join(step.command)

            result = self._controlled_executor.execute(
                ExecutionRequest(command=command)
            )

            results.append(result)

            self._remember_execution_result(
                command,
                result,
            )
            self._persist_execution_result(result)

            # Apenas comandos bloqueados interrompem o fluxo.
            if result.status is ExecutionStatus.BLOCKED:
                break

        self._clear_pending_execution()
        self._lifecycle = AgentLifecycle.COMPLETED

        return tuple(results)

    def _run_pipeline(
        self,
        request: str,
        context: ContextSnapshot,
    ) -> PipelineResult:
        """Run context-aware pipelines while preserving legacy test doubles."""

        run_method = self._execution_pipeline.run
        parameters = signature(run_method).parameters

        if "context" in parameters:
            return run_method(request, context=context)

        return run_method(request)

    def _persist_execution_result(self, result: ExecutionResult) -> None:
        """Persiste o resultado quando um serviço de memória está configurado."""

        if self._memory_service is None:
            return

        if self._pending_request is None or self._pending_context is None:
            raise RuntimeError("O contexto da execução pendente não está disponível.")

        self._memory_service.record_execution(
            session_id=self._session_id,
            user_request=self._pending_request,
            working_directory=self._pending_context.working_directory,
            project_name=self._pending_context.project_name,
            result=result,
        )

    def _clear_pending_execution(self) -> None:
        self._confirmation = None
        self._pipeline_result = None
        self._pending_request = None
        self._pending_context = None

    def _remember_execution_result(
        self,
        command: str,
        result: ExecutionResult,
    ) -> None:
        """Registra o resultado da execução no histórico da sessão."""

        status_description = {
            ExecutionStatus.APPROVED: "aprovada",
            ExecutionStatus.BLOCKED: "bloqueada",
            ExecutionStatus.EXECUTED: "executada",
            ExecutionStatus.FAILED: "falhou",
        }[result.status]

        self._session_manager.remember(
            f"Execução {status_description}: "
            f"{command} — {result.message}"
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
