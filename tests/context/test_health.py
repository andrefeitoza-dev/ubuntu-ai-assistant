import pytest

from ubuntu_ai.context import HealthStatus, SystemHealthService, SystemMetrics


def metrics(**changes: float | int) -> SystemMetrics:
    values: dict[str, float | int] = {
        "cpu_percent": 20.0,
        "memory_percent": 40.0,
        "memory_available_mb": 4096,
        "swap_percent": 0.0,
        "disk_percent": 50.0,
        "disk_free_gb": 100.0,
        "active_network_interfaces": 1,
        "process_count": 150,
        "uptime_seconds": 7200,
    }
    values.update(changes)
    return SystemMetrics(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("sample", "expected"),
    [
        (metrics(), HealthStatus.HEALTHY),
        (metrics(memory_percent=82.0), HealthStatus.ATTENTION),
        (metrics(cpu_percent=97.0), HealthStatus.CRITICAL),
        (metrics(disk_free_gb=0.5), HealthStatus.CRITICAL),
    ],
)
def test_classifies_system_health(sample: SystemMetrics, expected: HealthStatus) -> None:
    service = SystemHealthService(lambda: sample)

    assert service.snapshot().status is expected


def test_renders_compact_local_health_response() -> None:
    snapshot = SystemHealthService(lambda: metrics()).snapshot()

    text = snapshot.to_text()

    assert "saudável" in text
    assert "CPU: 20.0%" in text
    assert "RAM: 40.0%" in text
    assert "4096 MiB disponíveis" in text


def test_reports_unknown_when_metrics_are_unavailable() -> None:
    def fail() -> SystemMetrics:
        raise OSError("unavailable")

    snapshot = SystemHealthService(fail).snapshot()

    assert snapshot.status is HealthStatus.UNKNOWN
    assert "Não foi possível" in snapshot.to_text()
