from __future__ import annotations

import tkinter as tk
from pathlib import Path
from types import SimpleNamespace

from ubuntu_ai.gui import app as gui_app
from ubuntu_ai.interaction import ChatResponse


class FakeRoot:
    def __init__(self) -> None:
        self.calls: list[tuple[bool, object]] = []

    def iconphoto(self, default: bool, image: object) -> None:
        self.calls.append((default, image))


def make_app(candidates: tuple[Path, ...]):
    application = gui_app.UbuntuAIApp.__new__(gui_app.UbuntuAIApp)
    application.root = FakeRoot()
    application._icon_candidates = lambda: candidates
    return application


def test_window_icon_uses_first_valid_candidate(
    tmp_path: Path,
    monkeypatch,
) -> None:
    icon = tmp_path / "valid.png"
    icon.write_bytes(b"valid")
    loaded = SimpleNamespace(name="loaded")

    monkeypatch.setattr(gui_app.tk, "PhotoImage", lambda **_kwargs: loaded)
    application = make_app((icon,))

    application._set_window_icon()

    assert application._window_icon is loaded
    assert application.root.calls == [(True, loaded)]


def test_window_icon_skips_corrupt_candidate(
    tmp_path: Path,
    monkeypatch,
) -> None:
    corrupt = tmp_path / "corrupt.png"
    valid = tmp_path / "valid.png"
    corrupt.write_bytes(b"corrupt")
    valid.write_bytes(b"valid")
    loaded = SimpleNamespace(name="fallback")

    def load_image(*, file: Path):
        if file == corrupt:
            raise tk.TclError("corrupt image")
        return loaded

    monkeypatch.setattr(gui_app.tk, "PhotoImage", load_image)
    application = make_app((corrupt, valid))

    application._set_window_icon()

    assert application._window_icon is loaded
    assert application.root.calls == [(True, loaded)]


def test_window_icon_tolerates_missing_candidates(tmp_path: Path) -> None:
    application = make_app((tmp_path / "missing.png",))

    application._set_window_icon()

    assert application._window_icon is None
    assert application.root.calls == []


def test_friendly_error_explains_ollama_failure() -> None:
    message = gui_app.UbuntuAIApp._friendly_error("Ollama connection refused")

    assert "conectar ao Ollama" in message
    assert "serviço" in message


def test_friendly_error_explains_timeout() -> None:
    message = gui_app.UbuntuAIApp._friendly_error("request timed out")

    assert "tempo esperado" in message


def test_stale_snapshot_is_ignored() -> None:
    application = gui_app.UbuntuAIApp.__new__(gui_app.UbuntuAIApp)
    application._operation_generation = 2
    delivered: list[object] = []
    application._show_snapshot = delivered.append

    application._deliver_snapshot(1, SimpleNamespace())

    assert delivered == []


def test_current_snapshot_is_delivered() -> None:
    application = gui_app.UbuntuAIApp.__new__(gui_app.UbuntuAIApp)
    application._operation_generation = 2
    delivered: list[object] = []
    application._show_snapshot = delivered.append
    snapshot = SimpleNamespace()

    application._deliver_snapshot(2, snapshot)

    assert delivered == [snapshot]


def test_cancel_current_operation_invalidates_result(monkeypatch) -> None:
    application = gui_app.UbuntuAIApp.__new__(gui_app.UbuntuAIApp)
    application._busy = True
    application._operation_generation = 3
    cancel_calls: list[bool] = []
    application._backend = SimpleNamespace(
        cancel=lambda: cancel_calls.append(True),
    )
    messages: list[str] = []

    monkeypatch.setattr(
        application,
        "_set_busy",
        lambda busy: setattr(application, "_busy", busy),
    )
    monkeypatch.setattr(
        application,
        "_add_system_message",
        lambda message, **_kwargs: messages.append(message),
    )

    application.cancel_current_operation()

    assert application._busy is False
    assert application._operation_generation == 4
    assert cancel_calls == [True]
    assert "já pode enviar" in messages[0]


def test_chat_response_is_delivered(monkeypatch) -> None:
    application = gui_app.UbuntuAIApp.__new__(gui_app.UbuntuAIApp)
    application._operation_generation = 4
    application._busy = True
    messages: list[str] = []

    monkeypatch.setattr(application, "_set_busy", lambda busy: setattr(application, "_busy", busy))
    monkeypatch.setattr(
        application,
        "_add_system_message",
        lambda message, **_kwargs: messages.append(message),
    )

    application._deliver_chat(
        4,
        ChatResponse(content="Linux é um sistema operacional.", model="qwen2.5:3b"),
    )

    assert application._busy is False
    assert "Linux é um sistema" in messages[0]
    assert "Rota IA local" in messages[0]


def test_stale_chat_response_is_ignored(monkeypatch) -> None:
    application = gui_app.UbuntuAIApp.__new__(gui_app.UbuntuAIApp)
    application._operation_generation = 5
    messages: list[str] = []
    monkeypatch.setattr(
        application,
        "_add_system_message",
        lambda message, **_kwargs: messages.append(message),
    )

    application._deliver_chat(
        4,
        ChatResponse(content="Resposta antiga", model="qwen2.5:3b"),
    )

    assert messages == []


def test_duration_format_adapts_to_latency_scale() -> None:
    assert gui_app.UbuntuAIApp._format_duration(0.0004) == "400 µs"
    assert gui_app.UbuntuAIApp._format_duration(0.125) == "125.0 ms"
    assert gui_app.UbuntuAIApp._format_duration(2.5) == "2.50 s"


def test_automation_status_text_is_compact() -> None:
    assert (
        gui_app.UbuntuAIApp._automation_status_text(2, 5) == "Automações: 2 ativas · 5 concluídas"
    )
