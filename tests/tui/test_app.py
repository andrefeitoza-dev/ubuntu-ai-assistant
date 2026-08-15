from io import StringIO

from rich.console import Console

from ubuntu_ai.agent.models import AgentResult
from ubuntu_ai.agent_loop.models import (
    IterationRecord,
    LoopEvent,
    LoopSnapshot,
    LoopState,
    StopReason,
)
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.tui.app import TerminalApp


class FakeController:
    def __init__(self) -> None:
        self.started: list[str] = []
        self.confirmed = 0
        self.cancelled = 0
        self._snapshot = self._idle()

    def start(self, goal: str) -> LoopSnapshot:
        self.started.append(goal)
        self._snapshot = LoopSnapshot(
            goal=goal,
            state=LoopState.WAITING_CONFIRMATION,
            iteration=1,
            pending_plan=AgentResult(success=True, message="Plano de teste"),
            records=(),
            events=(
                LoopEvent(
                    iteration=1,
                    state=LoopState.WAITING_CONFIRMATION,
                    message="Aguardando confirmação.",
                ),
            ),
        )
        return self._snapshot

    def confirm(self) -> LoopSnapshot:
        self.confirmed += 1
        result = ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Executado.",
            command="echo ok",
        )
        record = IterationRecord(
            number=1,
            request="Mostre ok",
            plan_result=AgentResult(success=True, message="Plano de teste"),
            execution_results=(result,),
        )
        self._snapshot = LoopSnapshot(
            goal="Mostre ok",
            state=LoopState.COMPLETED,
            iteration=1,
            pending_plan=None,
            records=(record,),
            events=(
                LoopEvent(
                    iteration=1,
                    state=LoopState.COMPLETED,
                    message="Concluído com sucesso.",
                ),
            ),
            stop_reason=StopReason.GOAL_REACHED,
        )
        return self._snapshot

    def cancel(self) -> LoopSnapshot:
        self.cancelled += 1
        self._snapshot = LoopSnapshot(
            goal=self._snapshot.goal,
            state=LoopState.CANCELLED,
            iteration=self._snapshot.iteration,
            pending_plan=None,
            records=self._snapshot.records,
            events=(
                LoopEvent(
                    iteration=self._snapshot.iteration,
                    state=LoopState.CANCELLED,
                    message="Cancelado.",
                ),
            ),
            stop_reason=StopReason.USER_CANCELLED,
        )
        return self._snapshot

    def snapshot(self) -> LoopSnapshot:
        return self._snapshot

    @staticmethod
    def _idle() -> LoopSnapshot:
        return LoopSnapshot(
            goal="",
            state=LoopState.IDLE,
            iteration=0,
            pending_plan=None,
            records=(),
            events=(),
        )


class FakeMemoryService:
    def recent_executions(self, *, limit: int) -> tuple[object, ...]:
        assert limit == 10
        return ()


class FakePluginRegistry:
    def all(self) -> tuple[object, ...]:
        return ()


def test_terminal_app_runs_goal_confirms_and_quits() -> None:
    answers = iter(("Mostre ok", "s", ":quit"))
    output = StringIO()
    controller = FakeController()
    app = TerminalApp(
        controller=controller,  # type: ignore[arg-type]
        memory_service=FakeMemoryService(),  # type: ignore[arg-type]
        plugin_registry=FakePluginRegistry(),  # type: ignore[arg-type]
        console=Console(file=output, force_terminal=False, width=100),
        input_reader=lambda _: next(answers),
    )

    app.run()

    assert controller.started == ["Mostre ok"]
    assert controller.confirmed == 1
    assert "Plano de teste" in output.getvalue()
    assert "echo ok" in output.getvalue()
