from dataclasses import dataclass

from ubuntu_ai.reflection.v2_service import ReflectionV2Service


@dataclass
class FakeStatus:
    value: str


@dataclass
class FakeExecutionResult:
    status: FakeStatus
    message: str = ""
    stdout: str = ""
    stderr: str = ""


def test_service_reflects_existing_execution_result_shape() -> None:
    service = ReflectionV2Service()

    report = service.reflect_execution(
        FakeExecutionResult(
            status=FakeStatus("failed"),
            stderr="command not found",
        )
    )

    assert report.failure.failed
    assert len(service.history()) == 1


def test_service_limits_history() -> None:
    service = ReflectionV2Service(history_limit=2)

    for _ in range(3):
        service.reflect_execution(FakeExecutionResult(status=FakeStatus("executed")))

    assert len(service.history()) == 2
