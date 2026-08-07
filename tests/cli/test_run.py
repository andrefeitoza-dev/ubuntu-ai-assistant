from dataclasses import dataclass
from importlib import import_module

from typer.testing import CliRunner

from ubuntu_ai.cli.app import app

runner = CliRunner()
run_module = import_module("ubuntu_ai.cli.run")


@dataclass
class FakePending:
    pipeline_result: object | None = None


@dataclass
class FakeEvent:
    message: str


class FakeSnapshot:
    def __init__(
        self,
        *,
        requires_confirmation: bool,
        state,
        pending_plan=None,
        records=(),
        events=(),
    ) -> None:
        self.requires_confirmation = requires_confirmation
        self.state = state
        self.pending_plan = pending_plan
        self.records = records
        self.events = events
        self.iteration = 1
        self.goal = "status"
        self.stop_reason = None


class FakeRuntime:
    def __init__(self, waiting_state, completed_state) -> None:
        self.waiting_state = waiting_state
        self.completed_state = completed_state
        self.confirmed = 0
        self.cancelled = 0

    def start(self, goal: str):
        assert goal == "status"
        return self.waiting_state

    def confirm(self):
        self.confirmed += 1
        return self.completed_state

    def cancel(self):
        self.cancelled += 1
        return self.completed_state


def test_run_command_supports_dry_run(monkeypatch) -> None:
    from ubuntu_ai.agent_loop.models import LoopState
    from ubuntu_ai.agent.models import AgentResult

    waiting = FakeSnapshot(
        requires_confirmation=True,
        state=LoopState.WAITING_CONFIRMATION,
        pending_plan=AgentResult(
            success=True,
            message="Plano seguro",
        ),
    )
    completed = FakeSnapshot(
        requires_confirmation=False,
        state=LoopState.COMPLETED,
        events=(FakeEvent("Concluído"),),
    )
    runtime = FakeRuntime(waiting, completed)

    monkeypatch.setattr(
        run_module.container,
        "application_runtime",
        lambda: runtime,
    )

    result = runner.invoke(
        app,
        ["run", "--dry-run", "status"],
    )

    assert result.exit_code == 0
    assert "Plano seguro" in result.stdout
    assert "Dry-run" in result.stdout
    assert runtime.confirmed == 0


def test_run_command_can_auto_confirm(monkeypatch) -> None:
    from ubuntu_ai.agent_loop.models import LoopState
    from ubuntu_ai.agent.models import AgentResult

    waiting = FakeSnapshot(
        requires_confirmation=True,
        state=LoopState.WAITING_CONFIRMATION,
        pending_plan=AgentResult(
            success=True,
            message="Plano seguro",
        ),
    )
    completed = FakeSnapshot(
        requires_confirmation=False,
        state=LoopState.COMPLETED,
        events=(FakeEvent("Concluído"),),
    )
    runtime = FakeRuntime(waiting, completed)

    monkeypatch.setattr(
        run_module.container,
        "application_runtime",
        lambda: runtime,
    )

    result = runner.invoke(
        app,
        ["run", "--yes", "status"],
    )

    assert result.exit_code == 0
    assert runtime.confirmed == 1
    assert "concluído" in result.stdout.lower()
