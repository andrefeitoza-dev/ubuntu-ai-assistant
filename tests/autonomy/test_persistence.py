import stat
from datetime import UTC, datetime

import pytest

from ubuntu_ai.autonomy.long_tasks import LongTask, LongTaskManager, LongTaskStatus
from ubuntu_ai.autonomy.persistence import SQLiteAutomationRepository
from ubuntu_ai.autonomy.scheduler import AutomationRisk, ScheduledAutomation


def task() -> LongTask:
    return LongTask("t1", "g1", "Inventariar serviços", 4)


def test_repository_persists_checkpoint_and_history(tmp_path) -> None:
    repository = SQLiteAutomationRepository(tmp_path / "data" / "automation.db")
    manager = LongTaskManager(checkpoint=repository.save)
    manager.register(task())
    manager.start("t1")
    manager.advance("t1", completed_steps=2, message="metade")

    restored = SQLiteAutomationRepository(repository.database_path).get("t1")

    assert restored is not None
    assert restored.completed_steps == 2
    assert len(repository.history("t1")) == 3
    assert stat.S_IMODE(repository.database_path.stat().st_mode) == 0o600
    assert stat.S_IMODE(repository.database_path.parent.stat().st_mode) == 0o700


def test_interrupted_task_returns_to_pending(tmp_path) -> None:
    repository = SQLiteAutomationRepository(tmp_path / "automation.db")
    manager = LongTaskManager(checkpoint=repository.save)
    manager.register(task())
    manager.start("t1")

    recovered = repository.recover_interrupted()

    assert recovered[0].status is LongTaskStatus.PENDING
    assert "retomada segura" in recovered[0].message


def test_terminal_task_is_not_recovered(tmp_path) -> None:
    repository = SQLiteAutomationRepository(tmp_path / "automation.db")
    manager = LongTaskManager(checkpoint=repository.save)
    manager.register(task())
    manager.start("t1")
    manager.advance("t1", completed_steps=4, message="fim")

    assert repository.recover_interrupted() == ()


def test_checkpoint_rejects_apparent_secret(tmp_path) -> None:
    repository = SQLiteAutomationRepository(tmp_path / "automation.db")

    with pytest.raises(ValueError, match="secreto"):
        repository.save(LongTask("t1", "g1", "usar token=abc123", 1))


def test_repository_persists_schedules(tmp_path) -> None:
    repository = SQLiteAutomationRepository(tmp_path / "automation.db")
    schedule = ScheduledAutomation(
        "s1", "t1", datetime.now(UTC), AutomationRisk.HIGH, confirmed=True
    )

    repository.save_schedule(schedule)

    assert SQLiteAutomationRepository(repository.database_path).list_schedules() == (schedule,)
