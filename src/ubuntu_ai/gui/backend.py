from __future__ import annotations

from ubuntu_ai.agent_loop.models import LoopSnapshot
from ubuntu_ai.autonomy.long_tasks import LongTask
from ubuntu_ai.autonomy.observability import AutomationMetrics
from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.interaction import ChatResponse, InteractionDecision
from ubuntu_ai.remote.audit import RemoteAuditRecord
from ubuntu_ai.remote.diagnostics import RemoteDiagnosticService, RemoteSystemContext
from ubuntu_ai.remote.health import RemoteHealth, RemoteHealthService
from ubuntu_ai.remote.inventory import RemoteInventoryService
from ubuntu_ai.remote.models import RemoteHost


class GUIBackend:
    """Adapta o ApplicationRuntime para a interface gráfica."""

    def __init__(self) -> None:
        self._runtime = container.application_runtime()
        self._router = container.interaction_router()
        self._chat = container.chat_service()
        self._remote = self._runtime.remote
        self._inventory = RemoteInventoryService(self._remote.registry)
        self._selected_target = "local"

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

        return self._router.route(request)

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

    def automation_tasks(self) -> tuple[LongTask, ...]:
        return container.autonomous_runtime().long_tasks.all()

    def automation_metrics(self) -> AutomationMetrics:
        return container.autonomous_runtime().telemetry.metrics()
