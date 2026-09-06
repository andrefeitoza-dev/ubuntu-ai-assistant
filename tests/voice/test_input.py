from __future__ import annotations

from types import SimpleNamespace

import pytest

from ubuntu_ai.voice import VoiceInputService


def test_voice_is_optional_when_dependencies_are_missing(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("ubuntu_ai.voice.input.importlib.util.find_spec", lambda _name: None)

    availability = VoiceInputService(model_path=tmp_path / "model").availability()

    assert availability.available is False
    assert "opcional não instalado" in availability.message


def test_voice_requires_local_portuguese_model(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("ubuntu_ai.voice.input.importlib.util.find_spec", lambda _name: object())
    monkeypatch.setattr("ubuntu_ai.voice.input.ctypes.util.find_library", lambda _name: "lib")

    availability = VoiceInputService(model_path=tmp_path / "missing").availability()

    assert availability.available is False
    assert "Modelo de voz em português não encontrado" in availability.message


def test_voice_becomes_available_with_dependencies_and_model(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("ubuntu_ai.voice.input.importlib.util.find_spec", lambda _name: object())
    monkeypatch.setattr("ubuntu_ai.voice.input.ctypes.util.find_library", lambda _name: "lib")
    model = tmp_path / "model"
    model.mkdir()

    availability = VoiceInputService(model_path=model).availability()

    assert availability.available is True
    assert availability.model_path == model


def test_voice_reports_missing_native_audio_library(monkeypatch, tmp_path) -> None:
    monkeypatch.setattr("ubuntu_ai.voice.input.importlib.util.find_spec", lambda _name: object())
    monkeypatch.setattr("ubuntu_ai.voice.input.ctypes.util.find_library", lambda _name: None)

    availability = VoiceInputService(model_path=tmp_path / "model").availability()

    assert availability.available is False
    assert "libportaudio2" in availability.message


def test_recognizer_result_extracts_only_valid_text() -> None:
    assert VoiceInputService._result_text('{"text": "como está o computador"}') == (
        "como está o computador"
    )
    assert VoiceInputService._result_text('{"partial": "como"}') == ""
    assert VoiceInputService._result_text("invalid") == ""


def test_listen_captures_and_transcribes_local_audio(monkeypatch, tmp_path) -> None:
    model = tmp_path / "model"
    model.mkdir()
    service = VoiceInputService(model_path=model)
    monkeypatch.setattr(
        service,
        "availability",
        lambda: SimpleNamespace(available=True, message="pronto"),
    )

    class Stream:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self, _size):
            return b"audio", False

    class Recognizer:
        def AcceptWaveform(self, _data):
            return True

        def Result(self):
            return '{"text": "crie a pasta teste"}'

        def FinalResult(self):
            return '{"text": ""}'

    modules = {
        "sounddevice": SimpleNamespace(RawInputStream=lambda **_options: Stream()),
        "vosk": SimpleNamespace(
            Model=lambda _path: object(),
            KaldiRecognizer=lambda _model, _rate: Recognizer(),
        ),
    }
    monkeypatch.setattr(
        "ubuntu_ai.voice.input.importlib.import_module",
        lambda name: modules[name],
    )

    assert service.listen() == "crie a pasta teste"


def test_listen_reports_unavailable_input(monkeypatch, tmp_path) -> None:
    service = VoiceInputService(model_path=tmp_path / "missing")
    monkeypatch.setattr(
        service,
        "availability",
        lambda: SimpleNamespace(available=False, message="microfone indisponível"),
    )

    with pytest.raises(RuntimeError, match="microfone indisponível"):
        service.listen()
