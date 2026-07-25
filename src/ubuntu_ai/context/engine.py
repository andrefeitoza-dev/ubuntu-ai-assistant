from __future__ import annotations

from ubuntu_ai.agent.context import ContextProvider
from ubuntu_ai.agent.session import SessionManager
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.memory.models import ExecutionRecord
from ubuntu_ai.memory.service import MemoryService


class ContextEngine:
    """Builds contextual snapshots from environment, session and memory."""

    def __init__(
        self,
        *,
        context_provider: ContextProvider | None = None,
        session_manager: SessionManager | None = None,
        memory_service: MemoryService | None = None,
        history_limit: int = 5,
    ) -> None:
        if history_limit < 1:
            raise ValueError("O limite do histórico deve ser maior que zero.")

        self._context_provider = context_provider or ContextProvider()
        self._session_manager = session_manager or SessionManager()
        self._memory_service = memory_service
        self._history_limit = history_limit

    def build(self, *, session_id: str) -> ContextSnapshot:
        """Capture the current context without mutating session or memory."""

        if not session_id.strip():
            raise ValueError("O identificador da sessão não pode estar vazio.")

        environment = self._context_provider.get_context()
        executions = self._recent_executions(environment.project_name)

        return ContextSnapshot(
            session_id=session_id,
            working_directory=environment.working_directory,
            operating_system=environment.operating_system,
            project_name=environment.project_name,
            last_commands=tuple(record.command for record in executions),
            last_errors=self._extract_errors(executions),
            previous_request=self._previous_request(),
        )

    def _recent_executions(
        self,
        project_name: str | None,
    ) -> tuple[ExecutionRecord, ...]:
        if self._memory_service is None:
            return ()

        recent_executions = getattr(
            self._memory_service,
            "recent_executions",
            None,
        )
        if not callable(recent_executions):
            return ()

        return recent_executions(
            limit=self._history_limit,
            project_name=project_name,
        )

    def _previous_request(self) -> str | None:
        prefix = "Usuário: "

        for message in reversed(self._session_manager.session.history):
            if message.startswith(prefix):
                request = message.removeprefix(prefix).strip()
                return request or None

        return None

    @staticmethod
    def _extract_errors(
        executions: tuple[ExecutionRecord, ...],
    ) -> tuple[str, ...]:
        errors: list[str] = []

        for record in executions:
            if record.status != "failed" and not record.stderr.strip():
                continue

            detail = record.stderr.strip() or record.message.strip()
            if detail:
                errors.append(f"{record.command}: {detail}")

        return tuple(errors)
