from datetime import UTC, datetime
from pathlib import Path

import pytest

from ubuntu_ai.agent.context import AgentContext
from ubuntu_ai.agent.session import SessionManager
from ubuntu_ai.context.engine import ContextEngine
from ubuntu_ai.memory.models import ExecutionRecord


class FakeContextProvider:
    def get_context(self) -> AgentContext:
        return AgentContext(
            working_directory=Path("/tmp/project"),
            operating_system="Linux",
            project_name="project",
        )


class FakeMemoryService:
    def __init__(self, records: tuple[ExecutionRecord, ...]) -> None:
        self.records = records
        self.calls: list[dict[str, object]] = []

    def recent_executions(self, **kwargs: object) -> tuple[ExecutionRecord, ...]:
        self.calls.append(kwargs)
        return self.records


def make_record(
    *,
    command: str,
    status: str = "executed",
    message: str = "Executado.",
    stderr: str = "",
) -> ExecutionRecord:
    return ExecutionRecord(
        id=command,
        created_at=datetime.now(UTC),
        session_id="session-1",
        user_request="request",
        command=command,
        status=status,
        message=message,
        working_directory="/tmp/project",
        project_name="project",
        stderr=stderr,
    )


def test_context_engine_combines_environment_session_and_memory() -> None:
    session_manager = SessionManager()
    session_manager.remember("Usuário: primeira solicitação")
    session_manager.remember("Agente: resposta")

    memory_service = FakeMemoryService(
        (
            make_record(command="echo ok"),
            make_record(
                command="false",
                status="failed",
                stderr="command failed",
            ),
        )
    )
    engine = ContextEngine(
        context_provider=FakeContextProvider(),  # type: ignore[arg-type]
        session_manager=session_manager,
        memory_service=memory_service,  # type: ignore[arg-type]
    )

    snapshot = engine.build(session_id="session-1")

    assert snapshot.working_directory == Path("/tmp/project")
    assert snapshot.project_name == "project"
    assert snapshot.previous_request == "primeira solicitação"
    assert snapshot.last_commands == ("echo ok", "false")
    assert snapshot.last_errors == ("false: command failed",)
    assert memory_service.calls == [{"limit": 5, "project_name": "project"}]


def test_context_engine_works_without_memory() -> None:
    engine = ContextEngine(
        context_provider=FakeContextProvider(),  # type: ignore[arg-type]
    )

    snapshot = engine.build(session_id="session-1")

    assert snapshot.last_commands == ()
    assert snapshot.last_errors == ()
    assert snapshot.previous_request is None


def test_context_engine_rejects_empty_session_id() -> None:
    engine = ContextEngine()

    with pytest.raises(ValueError, match="sessão"):
        engine.build(session_id="   ")


def test_context_engine_rejects_invalid_history_limit() -> None:
    with pytest.raises(ValueError, match="histórico"):
        ContextEngine(history_limit=0)
