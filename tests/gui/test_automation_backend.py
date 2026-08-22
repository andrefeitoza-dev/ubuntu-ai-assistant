from types import SimpleNamespace

from ubuntu_ai.agents.selection import OrchestrationPlanner
from ubuntu_ai.gui import backend as gui_backend
from ubuntu_ai.remote.models import RemoteExecutionResult


def test_backend_exposes_automation_tasks_and_metrics(monkeypatch) -> None:
    tasks = (SimpleNamespace(task_id="t1"),)
    events = (SimpleNamespace(task_id="t1"),)
    metrics = SimpleNamespace(active_tasks=1, completed_tasks=0)
    calls: list[tuple[str, str]] = []
    autonomous = SimpleNamespace(
        long_tasks=SimpleNamespace(
            all=lambda: tasks,
            pause=lambda task_id: calls.append(("pause", task_id)),
            resume=lambda task_id: calls.append(("resume", task_id)),
            cancel=lambda task_id: calls.append(("cancel", task_id)),
        ),
        telemetry=SimpleNamespace(metrics=lambda: metrics, events=lambda: events),
    )
    monkeypatch.setattr(gui_backend.container, "autonomous_runtime", lambda: autonomous)
    backend = gui_backend.GUIBackend.__new__(gui_backend.GUIBackend)

    assert backend.automation_tasks() == tasks
    assert backend.automation_metrics() is metrics
    assert backend.automation_events() == events

    backend.pause_automation("t1")
    backend.resume_automation("t1")
    backend.cancel_automation("t1")

    assert calls == [("pause", "t1"), ("resume", "t1"), ("cancel", "t1")]


def test_backend_plans_multi_agent_for_selected_remote_target() -> None:
    backend = gui_backend.GUIBackend.__new__(gui_backend.GUIBackend)
    backend._selected_target = "servidor-tcc"

    goal = backend.plan_multi_agent(
        "diagnóstico completo",
        goal_id="goal-1",
    )

    assert goal.context["environment"] == "remote"
    assert goal.context["target"] == "servidor-tcc"
    assert len(goal.tasks) == 4
    assert all(task.payload.target == "servidor-tcc" for task in goal.tasks)


def test_backend_executes_confirmed_read_only_multi_agent_plan(monkeypatch) -> None:
    goal = OrchestrationPlanner().plan(
        "diagnóstico completo",
        goal_id="goal-local",
    )
    state = SimpleNamespace(completed_steps=0)

    class Manager:
        def start(self, task_id, message):
            return None

        def control(self, task_id):
            return SimpleNamespace(checkpoint=lambda: None)

        def advance(self, task_id, *, completed_steps, message):
            state.completed_steps = completed_steps

        def fail(self, task_id, reason):
            raise AssertionError(reason)

    autonomous = SimpleNamespace(long_tasks=Manager())
    monkeypatch.setattr(gui_backend.container, "autonomous_runtime", lambda: autonomous)
    monkeypatch.setattr(
        gui_backend,
        "build_specialist_orchestrator",
        lambda: SimpleNamespace(
            run=lambda _goal: SimpleNamespace(status=SimpleNamespace(value="completed"))
        ),
    )
    backend = gui_backend.GUIBackend.__new__(gui_backend.GUIBackend)
    backend._selected_target = "local"
    backend._remote = SimpleNamespace(
        execute=lambda host, command, confirmed: RemoteExecutionResult(
            host=host,
            command=command.argv,
            return_code=0,
            stdout="ok",
            stderr="",
        )
    )

    report = backend.execute_multi_agent(goal, confirmed=True)

    assert report.successful
    assert len(report.results) == 4
    assert state.completed_steps == 4
