import re
from pathlib import Path
from queue import SimpleQueue
from types import SimpleNamespace

from ubuntu_ai.gui.app import UbuntuAIApp


def test_worker_delivery_uses_main_thread_queue() -> None:
    calls = []
    scheduled = []

    application = UbuntuAIApp.__new__(UbuntuAIApp)
    application._ui_queue = SimpleQueue()
    application.root = SimpleNamespace(
        after=lambda delay, callback: scheduled.append((delay, callback))
    )

    application._post_to_ui(calls.append, "resultado")
    assert calls == []

    application._drain_ui_queue()

    assert calls == ["resultado"]
    assert scheduled
    assert scheduled[-1][0] == 25


def test_workers_do_not_call_zero_delay_tk_after_directly() -> None:
    source = Path("src/ubuntu_ai/gui/app.py").read_text(encoding="utf-8")

    assert re.search(r"self\.root\.after\(\s*0,", source) is None
    assert "self._post_to_ui(" in source
    assert "self._drain_ui_queue" in source
