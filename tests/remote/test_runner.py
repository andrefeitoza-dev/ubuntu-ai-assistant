import sys
import threading
import time

import pytest

from ubuntu_ai.remote.cancellation import (
    RemoteCancellationToken,
    RemoteExecutionCancelled,
)
from ubuntu_ai.remote.runner import ProcessRunner


def test_runner_enforces_timeout() -> None:
    with pytest.raises(TimeoutError, match="limite"):
        ProcessRunner().run(
            (sys.executable, "-c", "import time; time.sleep(2)"),
            timeout=0.05,
        )


def test_runner_terminates_cancelled_process() -> None:
    cancellation = RemoteCancellationToken()
    timer = threading.Timer(0.05, cancellation.cancel)
    timer.start()
    started = time.monotonic()

    try:
        with pytest.raises(RemoteExecutionCancelled):
            ProcessRunner().run(
                (sys.executable, "-c", "import time; time.sleep(5)"),
                timeout=10,
                cancellation=cancellation,
            )
    finally:
        timer.cancel()

    assert time.monotonic() - started < 2
