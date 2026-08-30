from __future__ import annotations

from dataclasses import dataclass, replace

from ubuntu_ai.agent_loop.models import LoopSnapshot
from ubuntu_ai.agents import default_agent_profiles
from ubuntu_ai.agents.orchestration import OrchestrationGoal
from ubuntu_ai.agents.selection import OrchestrationPlanner, build_specialist_orchestrator
from ubuntu_ai.agents.specialists import AgentEnvironment
from ubuntu_ai.audit import LocalActionAuditRecord
from ubuntu_ai.autonomy.control import TaskCancelledError
from ubuntu_ai.autonomy.long_tasks import LongTask
from ubuntu_ai.autonomy.observability import AutomationEvent, AutomationMetrics
from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.desktop import DesktopApplicationCatalog
from ubuntu_ai.diagnostics import SanitizedDiagnosticExporter
from ubuntu_ai.execution.mode import execution_mode
from ubuntu_ai.execution.permissions import capability_permissions
from ubuntu_ai.fast_path import CapabilityCatalog, CapabilityTopic, SystemFactResponder
from ubuntu_ai.gui.conversation_context import ReadOnlyConversationContext
from ubuntu_ai.gui.operational_queries import OperationalQueryResponder
from ubuntu_ai.interaction import ChatResponse, InteractionDecision, InteractionRoute
from ubuntu_ai.remote.audit import RemoteAuditRecord
from ubuntu_ai.remote.diagnostics import RemoteDiagnosticService, RemoteSystemContext
from ubuntu_ai.remote.health import RemoteHealth, RemoteHealthService
from ubuntu_ai.remote.inventory import RemoteInventoryService
from ubuntu_ai.remote.models import RemoteCommand, RemoteExecutionResult, RemoteHost


@dataclass(frozen=True, slots=True)
class MultiAgentExecutionReport:
    task_id: str
    goal_id: str
    target: str
    results: tuple[RemoteExecutionResult, ...]
    cancelled: bool = False

    @property
    def successful(self) -> bool:
        return not self.cancelled and all(result.success for result in self.results)


class GUIBackend:
    """Adapta o ApplicationRuntime para a interface gráfica."""

    def __init__(self) -> None:
        self._runtime = container.application_runtime()
        self._router = container.interaction_router()
        self._chat = container.chat_service()
        self._remote = self._runtime.remote
        self._inventory = RemoteInventoryService(self._remote.registry)
        self._selected_target = "local"
        self._capabilities = CapabilityCatalog()
        self._desktop_applications = DesktopApplicationCatalog()
        self._conversation_context = ReadOnlyConversationContext()
        self._diagnostic_exporter = SanitizedDiagnosticExporter()
        self._diagnostic_export_pending = False

    @property
    def selected_target(self) -> str:
        return self._selected_target

    @property
    def is_remote_selected(self) -> bool:
        return self._selected_target != "local"

    def remote_hosts(self) -> tuple[RemoteHost, ...]:
        return self._inventory.list_hosts()

    def select_target(self, name: str) -> RemoteHost:
        host = self._remote.registry.get(name)
        self._selected_target = host.name.lower()
        return host

    def register_remote_host(
        self,
        *,
        name: str,
        hostname: str,
        user: str | None,
        port: int,
        identity_file: str | None,
        known_hosts_file: str | None,
    ) -> RemoteHost:
        return self._inventory.register_ssh(
            name=name,
            hostname=hostname,
            user=user,
            port=port,
            identity_file=identity_file,
            known_hosts_file=known_hosts_file,
        )

    def remove_remote_host(self, name: str) -> RemoteHost:
        if name.strip().lower() == "local":
            raise ValueError("O computador local não pode ser removido.")
        removed = self._inventory.remove(name)
        if self._selected_target == removed.name.lower():
            self._selected_target = "local"
        return removed

    def test_remote_connection(self) -> RemoteHealth:
        host = self._require_remote_target()
        return RemoteHealthService().check(self._remote, host)

    def remote_diagnostics(self) -> RemoteSystemContext:
        host = self._require_remote_target()
        return RemoteDiagnosticService(self._remote).collect(host.name)

    def remote_audit_records(self) -> tuple[RemoteAuditRecord, ...]:
        return self._remote.audit_records(self._require_remote_target().name)

    def _require_remote_target(self) -> RemoteHost:
        if not self.is_remote_selected:
            raise ValueError("Selecione explicitamente um computador remoto.")
        return self._remote.registry.get(self._selected_target)

    def route(self, request: str) -> InteractionDecision:
        """Classifica a solicitação antes de acionar qualquer executor."""

        normalized_request = OperationalQueryResponder._normalize(request)
        if normalized_request in {"exporte um diagnostico", "exporte o diagnostico"}:
            self._diagnostic_export_pending = True
            return InteractionDecision(
                InteractionRoute.LOCAL,
                "Prévia: será criado em Downloads um JSON privado (0600) com versão, "
                "uso agregado e contagem da auditoria. Conversas, comandos e saídas não "
                "serão incluídos. Diga 'Confirme a exportação do diagnóstico' para gravar.",
            )
        if normalized_request == "cancele a exportacao do diagnostico":
            self._diagnostic_export_pending = False
            return InteractionDecision(InteractionRoute.LOCAL, "Exportação cancelada.")
        if normalized_request == "confirme a exportacao do diagnostico":
            if not self._diagnostic_export_pending:
                return InteractionDecision(
                    InteractionRoute.LOCAL,
                    "Não há exportação pendente. Solicite primeiro a prévia do diagnóstico.",
                )
            self._diagnostic_export_pending = False
            path = self._diagnostic_exporter.export(
                audit_records=self.local_action_audit_records(limit=100),
                simulation=execution_mode.simulation,
                denied_capabilities=capability_permissions.denied,
            )
            return InteractionDecision(
                InteractionRoute.LOCAL,
                f"Diagnóstico sanitizado exportado para {path}.",
            )
        permission_commands = {
            "aplicativos": "desktop",
            "arquivos": "files",
            "sistema": "system",
            "servicos": "services",
            "pacotes": "packages",
        }
        for label, capability in permission_commands.items():
            if normalized_request == f"bloqueie {label}":
                capability_permissions.set_allowed(capability, allowed=False)
                return InteractionDecision(
                    InteractionRoute.LOCAL,
                    f"Capacidade '{capability}' desativada nesta sessão.",
                )
            if normalized_request == f"permita {label}":
                capability_permissions.set_allowed(capability, allowed=True)
                return InteractionDecision(
                    InteractionRoute.LOCAL,
                    f"Capacidade '{capability}' reativada. A política central continua válida.",
                )
        if normalized_request == "mostre as permissoes do assistente":
            denied = capability_permissions.denied
            status = ", ".join(denied) if denied else "nenhuma capacidade adicional bloqueada"
            return InteractionDecision(InteractionRoute.LOCAL, f"Permissões da sessão: {status}.")

        if normalized_request in {"ative o modo de simulacao", "ativar modo de simulacao"}:
            execution_mode.set_simulation(True)
            return InteractionDecision(
                InteractionRoute.LOCAL,
                "Modo de simulação ativado. As ações serão validadas, mas não executadas.",
            )
        if normalized_request in {"desative o modo de simulacao", "desativar modo de simulacao"}:
            execution_mode.set_simulation(False)
            return InteractionDecision(
                InteractionRoute.LOCAL,
                "Modo de simulação desativado. As políticas e confirmações continuam ativas.",
            )
        if normalized_request in {"mostre o modo de execucao", "modo de simulacao"}:
            status = "ativado" if execution_mode.simulation else "desativado"
            return InteractionDecision(InteractionRoute.LOCAL, f"Modo de simulação: {status}.")

        contextual = self._conversation_context.resolve(
            request,
            target=self._selected_target,
        )
        if contextual.message is not None:
            return InteractionDecision(InteractionRoute.LOCAL, contextual.message)
        effective_request = contextual.request or request

        operational = OperationalQueryResponder()
        if operational.matches(effective_request):
            response = operational.respond(
                effective_request,
                tasks=self.automation_tasks(),
                schedules=self.automation_schedules(),
                profiles=default_agent_profiles(),
                plugins=container.plugin_registry().all(),
                audit_records=self.local_action_audit_records(limit=20),
                learning_stats=container.learning_service().stats(),
            )
            decision = InteractionDecision(InteractionRoute.LOCAL, response)
            self._remember_local_query(effective_request, decision)
            return decision

        if self.is_remote_selected and SystemFactResponder.matches(effective_request):
            return InteractionDecision(
                InteractionRoute.LOCAL,
                "A consulta se refere ao computador remoto "
                f"“{self._selected_target}”. Use Diagnosticar para coletar os "
                "dados por SSH; nenhuma informação do computador local foi exibida.",
            )
        decision = self._router.route(effective_request)
        self._remember_local_query(effective_request, decision)
        return decision

    def _remember_local_query(
        self,
        request: str,
        decision: InteractionDecision,
    ) -> None:
        if decision.route is InteractionRoute.LOCAL and decision.response:
            self._conversation_context.remember(request, target=self._selected_target)

    @staticmethod
    def is_system_fact_request(request: str) -> bool:
        return SystemFactResponder.matches(request)

    def selected_system_fact(self, request: str, *, target_name: str | None = None) -> str:
        """Consulta o destino selecionado sem misturar contexto local e remoto."""

        topic = SystemFactResponder.topic_for(request)
        if topic is None:
            raise ValueError("A solicitação não corresponde a um dado do computador.")

        target = (target_name or self._selected_target).strip().lower()
        if target == "local":
            decision = self._router.route(request)
            if decision.route is not InteractionRoute.LOCAL or decision.response is None:
                raise ValueError("Não foi possível consultar o computador local.")
            return decision.response

        host = self._remote.registry.get(target)
        return RemoteDiagnosticService(self._remote).answer_fact(host.name, topic)

    def capability_topics(self) -> tuple[CapabilityTopic, ...]:
        application_count = len(self._desktop_applications.applications)
        availability = (
            "Computador local com desktop · "
            f"{application_count} aplicativo(s) confiável(is) detectado(s)"
        )
        return tuple(
            replace(topic, availability=availability) if topic.code in {"12", "13", "20"} else topic
            for topic in self._capabilities.topics
        )

    def capability_detail(self, query: str) -> str:
        return self._capabilities.detail(query)

    def local_action_audit_records(
        self,
        *,
        limit: int = 100,
    ) -> tuple[LocalActionAuditRecord, ...]:
        """Expõe o histórico local somente para leitura pela interface."""

        return container.local_action_audit_service().records(limit=limit)

    def chat(self, request: str) -> ChatResponse:
        """Responde sem criar plano nem executar comandos."""

        return self._chat.ask(request)

    def start(self, request: str) -> LoopSnapshot:
        request = request.strip()

        if not request:
            raise ValueError("Digite uma solicitação.")

        return self._runtime.start(request)

    def confirm(self) -> LoopSnapshot:
        """Confirma explicitamente o plano atualmente pendente."""
        return self._runtime.confirm()

    def cancel(self) -> LoopSnapshot:
        """Cancela o plano atualmente pendente."""
        return self._runtime.cancel()

    def snapshot(self) -> LoopSnapshot:
        return self._runtime.snapshot()

    def has_pending_plan(self) -> bool:
        """Informa se uma ação aguarda decisão explícita do usuário."""

        return self.snapshot().requires_confirmation

    @staticmethod
    def is_confirm_pending_request(request: str) -> bool:
        return OperationalQueryResponder._normalize(request) in {
            "confirme o plano",
            "confirme o plano pendente",
            "pode executar o plano",
        }

    @staticmethod
    def is_cancel_pending_request(request: str) -> bool:
        return OperationalQueryResponder._normalize(request) in {
            "cancele o plano",
            "cancele o plano pendente",
            "nao execute o plano",
        }

    def automation_tasks(self) -> tuple[LongTask, ...]:
        return container.autonomous_runtime().long_tasks.all()

    def automation_schedules(self):
        return container.autonomous_runtime().scheduler.all()

    def automation_metrics(self) -> AutomationMetrics:
        return container.autonomous_runtime().telemetry.metrics()

    def automation_events(self) -> tuple[AutomationEvent, ...]:
        return container.autonomous_runtime().telemetry.events()

    def pause_automation(self, task_id: str) -> LongTask:
        return container.autonomous_runtime().long_tasks.pause(task_id)

    def resume_automation(self, task_id: str) -> LongTask:
        return container.autonomous_runtime().long_tasks.resume(task_id)

    def cancel_automation(self, task_id: str) -> LongTask:
        return container.autonomous_runtime().long_tasks.cancel(task_id)

    @staticmethod
    def is_remote_diagnostic_request(request: str) -> bool:
        normalized = OperationalQueryResponder._normalize(request)
        return normalized in {
            "diagnostique o servidor selecionado",
            "diagnostique o computador remoto selecionado",
            "faca um diagnostico do servidor escolhido",
            "faca um diagnostico do servidor selecionado",
        }

    @staticmethod
    def is_cancel_selected_automation_request(request: str) -> bool:
        normalized = OperationalQueryResponder._normalize(request)
        return normalized in {
            "cancele a tarefa selecionada",
            "cancele a automacao selecionada",
            "cancele a automacao escolhida",
            "cancele a tarefa escolhida",
        }

    def plan_multi_agent(self, request: str, *, goal_id: str) -> OrchestrationGoal:
        """Cria uma prévia somente leitura para o destino explicitamente selecionado."""

        environment = AgentEnvironment.REMOTE if self.is_remote_selected else AgentEnvironment.LOCAL
        target = self._selected_target if self.is_remote_selected else None
        return OrchestrationPlanner().plan(
            request,
            goal_id=goal_id,
            environment=environment,
            target=target,
        )

    @staticmethod
    def multi_agent_task_id(goal: OrchestrationGoal) -> str:
        return f"multi-agent-{goal.goal_id}"

    def register_multi_agent(self, goal: OrchestrationGoal) -> LongTask:
        """Registra a execução antes de iniciar a thread, tornando-a observável."""

        task = LongTask(
            task_id=self.multi_agent_task_id(goal),
            goal_id=goal.goal_id,
            description=goal.description,
            total_steps=len(goal.tasks),
            max_duration=300.0,
        )
        return container.autonomous_runtime().register_long_task(task)

    def execute_multi_agent(
        self,
        goal: OrchestrationGoal,
        *,
        confirmed: bool,
    ) -> MultiAgentExecutionReport:
        """Valida especialistas e executa apenas seus comandos limitados pela engine."""

        if not confirmed:
            raise PermissionError("A execução multiagente exige confirmação explícita.")

        validation = build_specialist_orchestrator().run(goal)
        if validation.status.value != "completed":
            raise PermissionError("O plano multiagente foi bloqueado pela política.")

        runtime = container.autonomous_runtime()
        task_id = self.multi_agent_task_id(goal)
        manager = runtime.long_tasks
        manager.start(task_id, "Especialistas iniciados.")
        control = manager.control(task_id)
        target = str(goal.context["target"])
        results: list[RemoteExecutionResult] = []

        try:
            for step, task in enumerate(goal.tasks, start=1):
                control.checkpoint()
                action = task.payload.actions[0]
                result = self._remote.execute(
                    target,
                    RemoteCommand(action.argv, timeout=30.0),
                    confirmed=confirmed,
                )
                control.checkpoint()
                results.append(result)
                if not result.success:
                    manager.fail(task_id, f"O agente {task.specialist.value} falhou.")
                    return MultiAgentExecutionReport(
                        task_id,
                        goal.goal_id,
                        target,
                        tuple(results),
                    )
                manager.advance(
                    task_id,
                    completed_steps=step,
                    message=f"Agente {task.specialist.value} concluído.",
                )
        except TaskCancelledError:
            manager.cancel(task_id)
            return MultiAgentExecutionReport(
                task_id,
                goal.goal_id,
                target,
                tuple(results),
                cancelled=True,
            )
        except Exception as exc:
            manager.fail(task_id, str(exc))
            raise

        return MultiAgentExecutionReport(
            task_id,
            goal.goal_id,
            target,
            tuple(results),
        )
