from ubuntu_ai.autonomy.long_tasks import LongTask, LongTaskManager
from ubuntu_ai.autonomy.observability import AutomationTelemetry


def test_telemetry_emits_events_and_metrics() -> None:
    telemetry = AutomationTelemetry()
    manager = LongTaskManager()
    manager.subscribe(telemetry.observe)
    manager.register(LongTask("t1", "g1", "inventário", 2))
    manager.start("t1")
    manager.advance("t1", completed_steps=2, message="concluído")

    metrics = telemetry.metrics()

    assert metrics.total_events == 3
    assert metrics.active_tasks == 0
    assert metrics.completed_tasks == 1
    assert metrics.average_progress == 1.0
    assert len(telemetry.events(task_id="t1")) == 3


def test_telemetry_respects_capacity() -> None:
    telemetry = AutomationTelemetry(capacity=2)
    manager = LongTaskManager()
    manager.subscribe(telemetry.observe)
    manager.register(LongTask("t1", "g1", "inventário", 2))
    manager.start("t1")
    manager.advance("t1", completed_steps=1, message="metade")

    assert len(telemetry.events()) == 2
