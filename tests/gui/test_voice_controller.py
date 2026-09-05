from __future__ import annotations

from types import SimpleNamespace

from ubuntu_ai.gui.voice_controller import VoiceControllerMixin


def test_transcription_is_processed_without_being_shown() -> None:
    events: list[tuple[str, object]] = []
    controller = VoiceControllerMixin()
    controller.voice_button = SimpleNamespace(
        configure=lambda **options: events.append(("button", options))
    )
    controller.status_label = SimpleNamespace(
        configure=lambda **options: events.append(("status", options))
    )
    controller.submit = lambda **options: events.append(("submit", options))

    controller._deliver_voice_text("como está o computador")

    assert (
        "submit",
        {
            "request_override": "como está o computador",
            "display_request": "Solicitação recebida por voz.",
        },
    ) in events
    assert "como está o computador" not in str(
        [value for name, value in events if name != "submit"]
    )
