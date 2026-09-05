from __future__ import annotations

import ctypes.util
import importlib
import importlib.util
import json
import os
from dataclasses import dataclass
from pathlib import Path
from time import monotonic

from ubuntu_ai.config.defaults import default_data_directory


@dataclass(frozen=True, slots=True)
class VoiceAvailability:
    available: bool
    message: str
    model_path: Path


class VoiceInputService:
    """Captura áudio em memória e transcreve localmente com Vosk."""

    SAMPLE_RATE = 16_000
    MAX_SECONDS = 7.0

    def __init__(self, *, model_path: Path | None = None) -> None:
        configured = os.environ.get("UBUNTU_AI_VOICE_MODEL", "").strip()
        selected = model_path or (
            Path(configured).expanduser()
            if configured
            else default_data_directory() / "voice" / "vosk-model-pt"
        )
        self._model_path = selected

    def availability(self) -> VoiceAvailability:
        missing = tuple(
            name
            for name in ("sounddevice", "vosk")
            if importlib.util.find_spec(name) is None
        )
        if missing:
            return VoiceAvailability(
                False,
                "Suporte de voz opcional não instalado: " + ", ".join(missing) + ".",
                self._model_path,
            )
        if ctypes.util.find_library("portaudio") is None:
            return VoiceAvailability(
                False,
                "Biblioteca de áudio PortAudio não encontrada. Instale libportaudio2.",
                self._model_path,
            )
        if not self._model_path.is_dir():
            return VoiceAvailability(
                False,
                f"Modelo de voz em português não encontrado em {self._model_path}.",
                self._model_path,
            )
        return VoiceAvailability(True, "Entrada por voz local disponível.", self._model_path)

    def listen(self) -> str:
        availability = self.availability()
        if not availability.available:
            raise RuntimeError(availability.message)

        sounddevice = importlib.import_module("sounddevice")
        vosk = importlib.import_module("vosk")
        recognizer = vosk.KaldiRecognizer(vosk.Model(str(self._model_path)), self.SAMPLE_RATE)
        started = monotonic()
        recognized: list[str] = []
        with sounddevice.RawInputStream(
            samplerate=self.SAMPLE_RATE,
            blocksize=4_000,
            dtype="int16",
            channels=1,
        ) as stream:
            while monotonic() - started < self.MAX_SECONDS:
                data, overflowed = stream.read(4_000)
                if overflowed:
                    continue
                if recognizer.AcceptWaveform(bytes(data)):
                    complete = self._result_text(recognizer.Result())
                    if complete:
                        recognized.append(complete)
                        break

        final = self._result_text(recognizer.FinalResult())
        if final:
            recognized.append(final)
        text = " ".join(recognized).strip()
        if not text:
            raise RuntimeError(
                "Não consegui reconhecer uma frase. Tente novamente mais perto do microfone."
            )
        return text

    @staticmethod
    def _result_text(result: str) -> str:
        try:
            payload = json.loads(result)
        except (json.JSONDecodeError, TypeError):
            return ""
        return str(payload.get("text", "")).strip()
