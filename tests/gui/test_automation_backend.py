from types import SimpleNamespace

from ubuntu_ai.gui import backend as gui_backend


def test_backend_exposes_automation_tasks_and_metrics(monkeypatch) -> None:
    tasks = (SimpleNamespace(task_id="t1"),)
    metrics = SimpleNamespace(active_tasks=1, completed_tasks=0)
    autonomous = SimpleNamespace(
        long_tasks=SimpleNamespace(all=lambda: tasks),
        telemetry=SimpleNamespace(metrics=lambda: metrics),
    )
    monkeypatch.setattr(gui_backend.container, "autonomous_runtime", lambda: autonomous)
    backend = gui_backend.GUIBackend.__new__(gui_backend.GUIBackend)

    assert backend.automation_tasks() == tasks
    assert backend.automation_metrics() is metrics
