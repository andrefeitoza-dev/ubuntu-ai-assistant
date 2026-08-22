from __future__ import annotations

import signal
from pathlib import Path

from ubuntu_ai.gui.single_instance import SingleInstance


def test_second_instance_activates_first(tmp_path: Path) -> None:
    lock_path = tmp_path / "assistant.lock"
    activated: list[bool] = []
    primary = SingleInstance(lock_path)
    secondary = SingleInstance(lock_path)

    try:
        assert primary.acquire_or_activate() is True
        primary.start(lambda: activated.append(True))

        assert secondary.acquire_or_activate() is False
        assert activated == [True]
    finally:
        secondary.close()
        primary.close()

    assert not lock_path.exists()


def test_lock_restores_previous_signal_handler(tmp_path: Path) -> None:
    lock_path = tmp_path / "assistant.lock"
    previous = signal.getsignal(signal.SIGUSR1)
    instance = SingleInstance(lock_path)

    try:
        assert instance.acquire_or_activate() is True
        instance.start(lambda: None)
        assert lock_path.read_text(encoding="utf-8").strip()
    finally:
        instance.close()

    assert signal.getsignal(signal.SIGUSR1) is previous
    assert not lock_path.exists()


def test_activation_before_gui_start_is_delivered_later(tmp_path: Path) -> None:
    lock_path = tmp_path / "assistant.lock"
    activated: list[bool] = []
    primary = SingleInstance(lock_path)
    secondary = SingleInstance(lock_path)

    try:
        assert primary.acquire_or_activate() is True
        assert secondary.acquire_or_activate() is False
        primary.start(lambda: activated.append(True))
        assert activated == [True]
    finally:
        secondary.close()
        primary.close()
