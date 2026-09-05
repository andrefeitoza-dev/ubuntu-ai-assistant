import threading
from pathlib import Path
from types import SimpleNamespace

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


def test_voice_output_ignores_empty_text() -> None:
    service = VoiceOutputService(executable="/usr/bin/spd-say")

    assert service.speak_async("   ") is False


def test_voice_output_invokes_local_synthesizer_without_shell(monkeypatch) -> None:
    calls: list[tuple[tuple[str, ...], dict[str, object]]] = []

    def run(arguments, **options):
        calls.append((arguments, options))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr("ubuntu_ai.voice.output.subprocess.run", run)

    VoiceOutputService(executable="/usr/bin/spd-say")._speak("Olá")

    assert calls == [(("/usr/bin/spd-say", "-l", "pt-BR", "Olá"), {"check": False, "timeout": 45})]


def test_voice_output_tolerates_synthesizer_failure(monkeypatch) -> None:
    def fail(*_args, **_kwargs):
        raise OSError("indisponível")

    monkeypatch.setattr("ubuntu_ai.voice.output.subprocess.run", fail)

    VoiceOutputService(executable="/usr/bin/spd-say")._speak("Olá")


def test_neural_voice_is_preferred_when_model_and_player_exist(tmp_path: Path, monkeypatch) -> None:
    model = tmp_path / "voice.onnx"
    model.touch()
    model.with_suffix(".onnx.json").touch()
    service = VoiceOutputService(model_path=model, player="/usr/bin/aplay")
    spoken: list[str] = []
    monkeypatch.setattr(service, "_piper_available", lambda: True)
    monkeypatch.setattr(service, "_speak_neural", spoken.append)

    service._speak("Olá")

    assert spoken == ["Olá"]
