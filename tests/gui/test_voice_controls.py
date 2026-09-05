from pathlib import Path
from types import SimpleNamespace

from ubuntu_ai.gui import voice_controls


def test_voice_controls_are_circular_accessible_and_have_tooltips() -> None:
    source = Path(voice_controls.__file__).read_text(encoding="utf-8")

    assert "create_oval(" in source
    assert 'takefocus=1' in source
    assert 'self.bind("<Return>"' in source
    assert 'self.bind("<space>"' in source
    assert "_show_tooltip" in source


def test_voice_output_active_state_uses_success_color() -> None:
    source = Path(voice_controls.__file__).read_text(encoding="utf-8")

    assert "fill=SUCCESS if active else self._base_fill" in source


def _button() -> tuple[voice_controls.CircularVoiceButton, list[tuple]]:
    events: list[tuple] = []
    button = object.__new__(voice_controls.CircularVoiceButton)
    button._enabled = True
    button._active = False
    button._symbol = "🎙"
    button._base_fill = "base"
    button._hover_fill = "hover"
    button._label = 1
    button._circle = 2
    button._command = lambda: events.append(("command",))
    button.configure = lambda **options: events.append(("configure", options))
    button.itemconfigure = lambda item, **options: events.append((item, options))
    button._show_tooltip = lambda: events.append(("show",))
    button._hide_tooltip = lambda: events.append(("hide",))
    return button, events


def test_circular_voice_button_updates_enabled_and_active_states() -> None:
    button, events = _button()

    button.set_enabled(False)
    assert button._activate() == "break"
    button.set_enabled(True)
    assert button._activate() == "break"
    button.set_active(True)

    assert ("command",) in events
    assert (2, {"fill": voice_controls.SUCCESS}) in events


def test_circular_voice_button_handles_hover_without_losing_active_state() -> None:
    button, events = _button()
    event = SimpleNamespace()

    button._enter(event)
    button._leave(event)
    button.set_active(True)
    button._enter(event)
    button._leave(event)

    assert (2, {"fill": "hover"}) in events
    assert (2, {"fill": voice_controls.SUCCESS}) in events
    assert ("show",) in events
    assert ("hide",) in events
