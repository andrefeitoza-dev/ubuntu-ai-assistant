from ubuntu_ai.hardening.health import ApplicationHealthService
from ubuntu_ai.hardening.models import HealthStatus


def test_health_service_reports_healthy_components() -> None:
    service = ApplicationHealthService()
    service.register("runtime", lambda: True)

    report = service.check()

    assert report.ready
    assert report.status is HealthStatus.HEALTHY


def test_health_service_reports_probe_exception_as_unhealthy() -> None:
    service = ApplicationHealthService()

    def failing_probe() -> bool:
        raise RuntimeError("offline")

    service.register("remote", failing_probe)

    report = service.check()

    assert not report.ready
    assert report.status is HealthStatus.UNHEALTHY
    assert report.components[0].message == "offline"
