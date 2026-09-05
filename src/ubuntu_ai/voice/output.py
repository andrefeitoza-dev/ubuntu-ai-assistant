from __future__ import annotations

import shutil
import subprocess
import threading


class VoiceOutputService:
    """Lê respostas pelo sintetizador local do Ubuntu, sem usar rede ou shell."""

    def __init__(self, executable: str | None = None) -> None:
        self._executable = shutil.which("spd-say") if executable is None else executable or None

    @property
    def available(self) -> bool:
        return self._executable is not None

    def speak_async(self, text: str) -> bool:
        if not self.available:
            return False
        spoken = text.split("\n\nRota ", 1)[0].strip()[:1200]
        if not spoken:
            return False
        threading.Thread(target=self._speak, args=(spoken,), daemon=True).start()
        return True

    def _speak(self, text: str) -> None:
        try:
            subprocess.run(
                (self._executable or "spd-say", "-l", "pt-BR", text),
                check=False,
                timeout=45,
            )
        except (OSError, subprocess.SubprocessError):
            return
