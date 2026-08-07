from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

from ubuntu_ai.agent_loop.controller import AgentLoopController
from ubuntu_ai.agent_loop.models import LoopSnapshot
from ubuntu_ai.autonomy.runtime import AutonomousRuntime
from ubuntu_ai.hardening.health import ApplicationHealthService
from ubuntu_ai.hardening.models import HealthReport, TelemetrySnapshot
from ubuntu_ai.hardening.telemetry import RuntimeTelemetry
from ubuntu_ai.logging.service import LoggingService
from ubuntu_ai.remote.engine import RemoteExecutionEngine
from ubuntu_ai.runtime_integration.runtime import MultiAgentRuntime

T = TypeVar("T")


class ApplicationRuntime:
    """Fachada canônica e observável da aplicação para a versão 1.0."""

    def __init__(
        self,
        *,
        controller: AgentLoopController,
        multi_agent: MultiAgentRuntime,
        autonomous: AutonomousRuntime,
        remote: RemoteExecutionEngine,
        telemetry: RuntimeTelemetry | None = None,
        health_service: ApplicationHealthService | None = None,
        logging_service: LoggingService | None = None,
    ) -> None:
        self._controller = controller
        self._multi_agent = multi_agent
        self._autonomous = autonomous
        self._remote = remote
        self._telemetry = telemetry or RuntimeTelemetry()
        self._health_service = health_service or ApplicationHealthService()
        self._logging_service = logging_service
        self._register_default_health_probes()

    @property
    def multi_agent(self) -> MultiAgentRuntime:
        return self._multi_agent

    @property
    def autonomous(self) -> AutonomousRuntime:
        return self._autonomous

    @property
    def remote(self) -> RemoteExecutionEngine:
        return self._remote

    def start(self, goal: str) -> LoopSnapshot:
        return self._observed(
            "application.start",
            lambda: self._controller.start(goal),
        )

    def confirm(self) -> LoopSnapshot:
        return self._observed(
            "application.confirm",
            self._controller.confirm,
        )

    def cancel(self) -> LoopSnapshot:
        return self._observed(
            "application.cancel",
            self._controller.cancel,
        )

    def snapshot(self) -> LoopSnapshot:
        return self._observed(
            "application.snapshot",
            self._controller.snapshot,
        )

    def run(
        self,
        goal: str,
        *,
        auto_confirm: bool = False,
    ) -> LoopSnapshot:
        snapshot = self.start(goal)

        while auto_confirm and snapshot.requires_confirmation:
            snapshot = self.confirm()

        return snapshot

    def telemetry(self) -> TelemetrySnapshot:
        return self._telemetry.snapshot()

    def health(self) -> HealthReport:
        return self._health_service.check()

    def _observed(
        self,
        operation: str,
        action: Callable[[], T],
    ) -> T:
        logger = (
            self._logging_service.get_logger("application")
            if self._logging_service is not None
            else None
        )

        with self._telemetry.measure(operation):
            try:
                result = action()
            except Exception:
                if logger is not None:
                    logger.exception("Falha na operação %s.", operation)
                raise

        if logger is not None:
            logger.debug("Operação concluída: %s", operation)

        return result

    def _register_default_health_probes(self) -> None:
        probes = {
            "agent-loop": lambda: self._controller is not None,
            "multi-agent": lambda: self._multi_agent is not None,
            "autonomous": lambda: self._autonomous is not None,
            "remote": lambda: self._remote is not None,
        }

        for name, probe in probes.items():
            try:
                self._health_service.register(name, probe)
            except ValueError:
                continue
