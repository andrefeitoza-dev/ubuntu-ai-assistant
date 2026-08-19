import pytest

from ubuntu_ai.autonomy.long_tasks import LongTask, LongTaskManager, LongTaskStatus


def task(*, max_duration: float = 60.0) -> LongTask:
    return LongTask(
        task_id="task-1",
        goal_id="goal-1",
        description="Inventariar serviços",
        total_steps=4,
        max_duration=max_duration,
    )


def test_long_task_reports_incremental_progress() -> None:
    manager = LongTaskManager()
    events: list[LongTask] = []
    manager.subscribe(events.append)
    manager.register(task())
    manager.start("task-1")

    updated = manager.advance(
        "task-1",
        completed_steps=2,
        message="Serviços verificados.",
    )

    assert updated.status is LongTaskStatus.RUNNING
    assert updated.progress == 0.5
    assert events[-1] == updated


def test_long_task_completes_at_total_steps() -> None:
    manager = LongTaskManager()
    manager.register(task())
    manager.start("task-1")

    completed = manager.advance(
        "task-1",
        completed_steps=4,
        message="Inventário concluído.",
    )

    assert completed.terminal
    assert completed.status is LongTaskStatus.COMPLETED
    assert completed.progress == 1.0


def test_long_task_can_pause_resume_and_cancel() -> None:
    manager = LongTaskManager()
    manager.register(task())
    manager.start("task-1")

    assert manager.pause("task-1").status is LongTaskStatus.PAUSED
    assert manager.control("task-1").paused
    assert manager.resume("task-1").status is LongTaskStatus.RUNNING

    cancelled = manager.cancel("task-1")

    assert cancelled.status is LongTaskStatus.CANCELLED
    assert manager.control("task-1").cancelled
    assert manager.active() == ()


def test_long_task_enforces_duration_limit() -> None:
    now = [100.0]
    manager = LongTaskManager(clock=lambda: now[0])
    manager.register(task(max_duration=10.0))
    manager.start("task-1")
    now[0] = 111.0

    timed_out = manager.enforce_limits("task-1")

    assert timed_out.status is LongTaskStatus.TIMED_OUT
    assert manager.control("task-1").cancelled


def test_progress_cannot_retrocede() -> None:
    manager = LongTaskManager()
    manager.register(task())
    manager.start("task-1")
    manager.advance("task-1", completed_steps=2, message="metade")

    with pytest.raises(ValueError, match="retroceder"):
        manager.advance("task-1", completed_steps=1, message="inválido")


def test_duplicate_task_is_rejected() -> None:
    manager = LongTaskManager()
    manager.register(task())

    with pytest.raises(ValueError, match="já registrada"):
        manager.register(task())
