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


def test_remote_button_keeps_selected_target_visible() -> None:
    assert gui_app.UbuntuAIApp._remote_button_text("local", expanded=False) == (
        "Computador: local  ▾"
    )
    assert gui_app.UbuntuAIApp._remote_button_text("servidor-tcc", expanded=True) == (
        "Computador: servidor-tcc  ▴"
    )


def test_gui_exposes_capability_catalog_button() -> None:
    source = Path(gui_app.__file__).read_text(encoding="utf-8")

    assert 'text="Recursos e ajuda  ▾"' in source
    assert "tk.Listbox(" in source
    assert "_build_capabilities_panel" in source
    assert "_schedule_capability_detail" in source
    assert "_send_resource_to_conversation" in source
    assert "panel.place(" in source
    assert "panel.place_forget()" in source
    assert "tk.Menu(" not in source
    assert "tk.Toplevel(" not in source


def test_gui_uses_readable_conversation_typography() -> None:
    assert gui_app.FONT_BODY == ("Sans", 12)
    assert gui_app.FONT_BODY_BOLD == ("Sans", 12, "bold")
    assert gui_app.FONT_SMALL == ("Sans", 11)
    assert gui_app.FONT_TINY == ("Sans", 10)
    assert gui_app.FONT_MONO == ("Monospace", 11)

    source = Path(gui_app.__file__).read_text(encoding="utf-8")
    assert "font=FONT_BODY" in source
    assert "font=FONT_TITLE" in source
    assert "font=FONT_HERO" in source


def test_capability_panel_closes_without_blocking_computer_controls() -> None:
    source = Path(gui_app.__file__).read_text(encoding="utf-8")

    toggle_start = source.index("    def _toggle_remote_controls")
    toggle_end = source.index("\n    def ", toggle_start + 5)
    toggle_source = source[toggle_start:toggle_end]

    assert "_hide_capabilities_panel()" in toggle_source
    assert '"<Escape>"' in source
    assert '"<Unmap>"' in source
    assert "_close_capabilities_on_outside_click" in source
    assert "140," in source


def test_selected_resource_is_added_to_conversation() -> None:
    application = gui_app.UbuntuAIApp.__new__(gui_app.UbuntuAIApp)
    messages: list[tuple[str, str]] = []
    focused: list[bool] = []

    application._backend = SimpleNamespace(
        capability_detail=lambda code: f"Detalhes de {code}",
    )
    application._resources_panel = None
    application._resource_hover_after_id = None
    application._add_system_message = lambda message, color: messages.append((message, color))
    application.request_entry = SimpleNamespace(
        focus_set=lambda: focused.append(True),
        winfo_exists=lambda: True,
    )

    application._send_resource_to_conversation("08")

    assert messages == [("Detalhes de 08\n\nRota local · recursos", gui_app.TEXT)]
    assert focused == [True]


def test_remote_system_fact_runs_outside_the_gui_thread() -> None:
    source = Path(gui_app.__file__).read_text(encoding="utf-8")

    assert "_backend.is_system_fact_request(request)" in source
    assert "target=self._start_selected_system_fact" in source
    assert "target_name=target" in source
    assert "Rota SSH somente leitura" in source


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


def test_mousewheel_supports_linux_buttons() -> None:
    assert gui_app.UbuntuAIApp._mousewheel_units(delta=0, button=4) == -3
    assert gui_app.UbuntuAIApp._mousewheel_units(delta=0, button=5) == 3


def test_mousewheel_supports_delta_events() -> None:
    assert gui_app.UbuntuAIApp._mousewheel_units(delta=120, button=0) == -1
    assert gui_app.UbuntuAIApp._mousewheel_units(delta=-120, button=0) == 1
    assert gui_app.UbuntuAIApp._mousewheel_units(delta=0, button=0) == 0


def test_mousewheel_scrolls_conversation_canvas() -> None:
    application = gui_app.UbuntuAIApp.__new__(gui_app.UbuntuAIApp)
    calls: list[tuple[int, str]] = []
    application.canvas = SimpleNamespace(
        yview_scroll=lambda units, mode: calls.append((units, mode))
    )

    result = application._on_mousewheel(SimpleNamespace(delta=0, num=5))

    assert result == "break"
    assert calls == [(3, "units")]


def test_computer_controls_close_when_user_clicks_outside() -> None:
    source = Path(gui_app.__file__).read_text(encoding="utf-8")

    assert "def _hide_remote_controls" in source
    assert "inside_remote_controls" in source
    assert "if self._remote_controls_visible and not inside_remote_controls:" in source
    assert "self._hide_remote_controls()" in source
