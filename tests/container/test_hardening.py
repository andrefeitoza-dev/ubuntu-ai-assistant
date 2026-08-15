from ubuntu_ai.container import Container
from ubuntu_ai.hardening.health import ApplicationHealthService
from ubuntu_ai.hardening.telemetry import RuntimeTelemetry
from ubuntu_ai.logging import LoggingService


def test_container_composes_hardening_services_as_singletons() -> None:
    container = Container()

    assert isinstance(container.runtime_telemetry(), RuntimeTelemetry)
    assert container.runtime_telemetry() is container.runtime_telemetry()

    assert isinstance(
        container.application_health_service(),
        ApplicationHealthService,
    )
    assert container.application_health_service() is container.application_health_service()

    assert isinstance(container.logging_service(), LoggingService)
    assert container.logging_service() is container.logging_service()
