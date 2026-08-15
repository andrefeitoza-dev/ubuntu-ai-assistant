import pytest

from ubuntu_ai.hardening.telemetry import RuntimeTelemetry


def test_telemetry_records_calls_and_duration() -> None:
    telemetry = RuntimeTelemetry()

    with telemetry.measure("planner"):
        pass

    metric = telemetry.snapshot().metrics[0]

    assert metric.operation == "planner"
    assert metric.calls == 1
    assert metric.failures == 0
    assert metric.total_duration >= 0


def test_telemetry_records_failures_without_swallowing_error() -> None:
    telemetry = RuntimeTelemetry()

    with pytest.raises(RuntimeError):
        with telemetry.measure("executor"):
            raise RuntimeError("boom")

    metric = telemetry.snapshot().metrics[0]
    assert metric.failures == 1
