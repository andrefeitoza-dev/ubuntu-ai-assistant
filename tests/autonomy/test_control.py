from threading import Thread
from time import sleep

import pytest

from ubuntu_ai.autonomy.control import TaskCancelledError, TaskControl


def test_cancelled_checkpoint_raises() -> None:
    control = TaskControl()
    control.cancel()

    with pytest.raises(TaskCancelledError, match="cancelada"):
        control.checkpoint()


def test_paused_checkpoint_resumes_cooperatively() -> None:
    control = TaskControl()
    completed: list[bool] = []
    control.pause()

    worker = Thread(target=lambda: (control.checkpoint(), completed.append(True)))
    worker.start()
    sleep(0.01)

    assert completed == []

    control.resume()
    worker.join(timeout=1)

    assert completed == [True]


def test_cancel_releases_paused_worker() -> None:
    control = TaskControl()
    cancelled: list[bool] = []
    control.pause()

    def worker_action() -> None:
        try:
            control.checkpoint()
        except TaskCancelledError:
            cancelled.append(True)

    worker = Thread(target=worker_action)
    worker.start()
    sleep(0.01)
    control.cancel()
    worker.join(timeout=1)

    assert cancelled == [True]
