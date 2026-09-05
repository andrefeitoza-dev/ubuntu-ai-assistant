import threading

from ubuntu_ai.voice import VoiceOutputService


def test_voice_output_is_optional_without_local_synthesizer() -> None:
    service = VoiceOutputService(executable="")

    assert service.available is False
    assert service.speak_async("Olá") is False


def test_voice_output_removes_route_metadata_and_limits_text(monkeypatch) -> None:
    spoken: list[str] = []
    completed = threading.Event()
    service = VoiceOutputService(executable="/usr/bin/spd-say")
    monkeypatch.setattr(
        service,
        "_speak",
        lambda text: (spoken.append(text), completed.set()),
    )

    assert service.speak_async("Resposta útil.\n\nRota IA local · modelo") is True

    assert completed.wait(1)
    assert spoken == ["Resposta útil."]
