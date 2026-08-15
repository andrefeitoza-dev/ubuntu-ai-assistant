from ubuntu_ai.execution.execution_report import ExecutionReport
from ubuntu_ai.execution.models import (
    ExecutionResult,
    ExecutionStatus,
)


def test_execution_report_calculates_statistics() -> None:
    results = (
        ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Comando executado.",
            command="pwd",
            return_code=0,
            duration=0.2,
        ),
        ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Comando executado.",
            command="whoami",
            return_code=0,
            duration=0.3,
        ),
        ExecutionResult(
            status=ExecutionStatus.FAILED,
            message="O comando falhou.",
            command="false",
            return_code=1,
            duration=0.1,
        ),
        ExecutionResult(
            status=ExecutionStatus.BLOCKED,
            message="Comando bloqueado.",
            command="rm -rf /",
        ),
        ExecutionResult(
            status=ExecutionStatus.APPROVED,
            message="Comando autorizado.",
            command="echo hello",
        ),
    )

    report = ExecutionReport.from_results(results)

    assert report.results == results
    assert report.statistics.total == 5
    assert report.statistics.executed == 2
    assert report.statistics.failed == 1
    assert report.statistics.blocked == 1
    assert report.statistics.approved == 1
    assert report.statistics.total_duration == 0.6


def test_execution_report_is_successful_without_failures_or_blocks() -> None:
    results = (
        ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Comando executado.",
            command="pwd",
            return_code=0,
        ),
        ExecutionResult(
            status=ExecutionStatus.APPROVED,
            message="Comando autorizado.",
            command="whoami",
        ),
    )

    report = ExecutionReport.from_results(results)

    assert report.successful is True


def test_execution_report_is_not_successful_when_command_fails() -> None:
    results = (
        ExecutionResult(
            status=ExecutionStatus.FAILED,
            message="O comando falhou.",
            command="false",
            return_code=1,
        ),
    )

    report = ExecutionReport.from_results(results)

    assert report.successful is False


def test_execution_report_is_not_successful_when_command_is_blocked() -> None:
    results = (
        ExecutionResult(
            status=ExecutionStatus.BLOCKED,
            message="Comando bloqueado.",
            command="rm -rf /",
        ),
    )

    report = ExecutionReport.from_results(results)

    assert report.successful is False


def test_execution_report_handles_empty_results() -> None:
    report = ExecutionReport.from_results(())

    assert report.results == ()
    assert report.statistics.total == 0
    assert report.statistics.approved == 0
    assert report.statistics.blocked == 0
    assert report.statistics.executed == 0
    assert report.statistics.failed == 0
    assert report.statistics.total_duration == 0.0
    assert report.successful is True


def test_execution_report_ignores_missing_duration() -> None:
    results = (
        ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Comando executado.",
            duration=0.4,
        ),
        ExecutionResult(
            status=ExecutionStatus.EXECUTED,
            message="Comando executado.",
            duration=None,
        ),
    )

    report = ExecutionReport.from_results(results)

    assert report.statistics.total_duration == 0.4
