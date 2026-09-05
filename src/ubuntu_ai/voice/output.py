from __future__ import annotations

import shutil
import subprocess
import tempfile
import threading
import wave
from pathlib import Path

from ubuntu_ai.config.defaults import default_data_directory


class VoiceOutputService:
    """Lê respostas pelo sintetizador local do Ubuntu, sem usar rede ou shell."""

    def __init__(
        self,
        executable: str | None = None,
        *,
        model_path: Path | None = None,
        player: str | None = None,
    ) -> None:
        self._executable = shutil.which("spd-say") if executable is None else executable or None
        default_model = default_data_directory() / "voice" / "piper" / "pt_BR-cadu-medium.onnx"
        self._model_path = (
            Path("/__ubuntu_ai_neural_voice_disabled__")
            if executable is not None and model_path is None
            else model_path or default_model
        )
        self._player = shutil.which("aplay") if player is None else player or None

    @property
    def available(self) -> bool:
        return self.neural_available or self._executable is not None

    @property
    def neural_available(self) -> bool:
        return (
            self._player is not None
            and self._model_path.is_file()
            and self._model_path.with_suffix(".onnx.json").is_file()
            and self._piper_available()
        )

    @staticmethod
    def _piper_available() -> bool:
        try:
            import piper  # noqa: F401
        except ImportError:
            return False
        return True

    def speak_async(self, text: str) -> bool:
        if not self.available:
            return False
        spoken = text.split("\n\nRota ", 1)[0].strip()[:1200]
        if not spoken:
            return False
        threading.Thread(target=self._speak, args=(spoken,), daemon=True).start()
        return True

    def _speak(self, text: str) -> None:
        if self.neural_available:
            self._speak_neural(text)
            return
        try:
            subprocess.run(
                (self._executable or "spd-say", "-l", "pt-BR", text),
                check=False,
                timeout=45,
            )
        except (OSError, subprocess.SubprocessError):
            return

    def _speak_neural(self, text: str) -> None:
        from piper import PiperVoice

        try:
            voice = PiperVoice.load(str(self._model_path))
            with tempfile.NamedTemporaryFile(suffix=".wav") as audio:
                with wave.open(audio.name, "wb") as wav_file:
                    voice.synthesize_wav(text, wav_file)
                subprocess.run(
                    (self._player or "aplay", "-q", audio.name),
                    check=False,
                    timeout=90,
                )
        except (OSError, RuntimeError, subprocess.SubprocessError):
            return
