from dataclasses import dataclass

import pytest

from ubuntu_ai.application.runtime import ApplicationRuntime
from ubuntu_ai.hardening.models import HealthStatus


@dataclass
class FakeSnapshot:
    requires_confirmation: bool = False


class Controller:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail

    def start(self, goal):
        if self.fail:
            raise RuntimeError("failed")
        return FakeSnapshot()

    def confirm(self):
        return FakeSnapshot()

    def cancel(self):
        return FakeSnapshot()

    def snapshot(self):
        return FakeSnapshot()


def build_runtime(*, fail: bool = False) -> ApplicationRuntime:
    return ApplicationRuntime(
        controller=Controller(fail=fail),
        multi_agent=object(),
        autonomous=object(),
        remote=object(),
    )


def test_runtime_exposes_health_report() -> None:
    report = build_runtime().health()

    assert report.ready
    assert report.status is HealthStatus.HEALTHY
    assert len(report.components) == 4


def test_runtime_records_successful_operation() -> None:
    runtime = build_runtime()

    runtime.start("status")

    metric = runtime.telemetry().metrics[0]
    assert metric.operation == "application.start"
    assert metric.calls == 1
    assert metric.failures == 0


def test_runtime_records_failed_operation() -> None:
    runtime = build_runtime(fail=True)

    with pytest.raises(RuntimeError):
        runtime.start("status")

    metric = runtime.telemetry().metrics[0]
    assert metric.failures == 1
