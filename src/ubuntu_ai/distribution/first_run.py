from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass

DEFAULT_MODEL = "qwen2.5:3b"
OLLAMA_INSTALL_URL = "https://docs.ollama.com/linux"


@dataclass(frozen=True, slots=True)
class FirstRunStatus:
    ollama_available: bool
    ollama_running: bool
    model_available: bool
    model: str = DEFAULT_MODEL

    @property
    def ready(self) -> bool:
        return self.ollama_available and self.ollama_running and self.model_available


class FirstRunSetup:
    """Verifica e prepara o runtime local sem usar shell ou elevação automática."""

    def __init__(self, *, executable: str | None = None, model: str = DEFAULT_MODEL) -> None:
        self._executable = shutil.which("ollama") if executable is None else executable
        self._model = model

    def status(self) -> FirstRunStatus:
        if not self._executable:
            return FirstRunStatus(False, False, False, self._model)

        running = self._run("list").returncode == 0
        model_available = running and self._run("show", self._model).returncode == 0
        return FirstRunStatus(True, running, model_available, self._model)

    def pull_model(self) -> subprocess.CompletedProcess[str]:
        if not self._executable:
            raise RuntimeError("Ollama não encontrado. Instale o Ollama antes de baixar o modelo.")
        return self._run("pull", self._model)

    def _run(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        assert self._executable is not None
        return subprocess.run(
            (self._executable, *arguments),
            check=False,
            capture_output=True,
            text=True,
            shell=False,
            timeout=1800,
        )
