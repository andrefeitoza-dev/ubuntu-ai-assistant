from ubuntu_ai.agent_loop import LoopWatchdog
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus


def test_watchdog_detects_repeated_result() -> None:
    watchdog = LoopWatchdog(max_stalled_iterations=1)
    results = (
        ExecutionResult(
            status=ExecutionStatus.FAILED,
            message="same failure",
            command="false",
            return_code=1,
        ),
    )

    assert watchdog.observe(results) is False
    assert watchdog.observe(results) is True
