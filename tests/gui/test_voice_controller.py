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


def test_user_can_enable_and_disable_spoken_responses() -> None:
    spoken: list[str] = []
    labels: list[dict[str, str]] = []
    controller = VoiceControllerMixin()
    controller._voice_output = SimpleNamespace(
        available=True,
        speak_async=spoken.append,
    )
    controller.speech_button = SimpleNamespace(
        configure=lambda **options: labels.append(options)
    )

    controller._toggle_speech_output()
    controller._speak_response("Resposta do assistente")
    controller._toggle_speech_output()
    controller._speak_response("Não deve ser lida")

    assert [label["text"] for label in labels] == ["voice output", "voice output"]
    assert spoken == ["Voz do assistente ativada.", "Resposta do assistente"]


def test_unavailable_spoken_voice_shows_local_install_hint() -> None:
    messages: list[tuple[str, str]] = []
    controller = VoiceControllerMixin()
    controller._voice_output = SimpleNamespace(available=False)
    controller._add_system_message = lambda message, color: messages.append((message, color))

    controller._toggle_speech_output()

    assert "speech-dispatcher" in messages[0][0]
