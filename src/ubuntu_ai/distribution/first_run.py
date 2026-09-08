from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass, replace

from ubuntu_ai.config import ConfigRepository

DEFAULT_MODEL = "qwen2.5:3b"
OLLAMA_INSTALL_URL = "https://docs.ollama.com/linux"


@dataclass(frozen=True, slots=True)
class FirstRunStatus:
    ollama_available: bool
    ollama_running: bool
    model_available: bool
    model: str = DEFAULT_MODEL
    models: tuple[str, ...] = ()

    @property
    def ready(self) -> bool:
        return self.ollama_available and self.ollama_running and self.model_available


class FirstRunSetup:
    """Verifica e prepara o runtime local sem usar shell ou elevação automática."""

    def __init__(
        self,
        *,
        executable: str | None = None,
        model: str | None = None,
        config_repository: ConfigRepository | None = None,
    ) -> None:
        self._executable = shutil.which("ollama") if executable is None else executable
        self._config_repository = config_repository or ConfigRepository()
        self._model = model or self._configured_model()

    @property
    def model(self) -> str:
        return self._model

    def status(self) -> FirstRunStatus:
        if not self._executable:
            return FirstRunStatus(False, False, False, self._model)

        listing = self._run("list")
        running = listing.returncode == 0
        models = self._parse_models(listing.stdout) if running else ()
        model_available = running and self._run("show", self._model).returncode == 0
        return FirstRunStatus(True, running, model_available, self._model, models)

    def list_models(self) -> tuple[str, ...]:
        if not self._executable:
            return ()
        result = self._run("list")
        return self._parse_models(result.stdout) if result.returncode == 0 else ()

    def select_model(self, model: str) -> None:
        normalized = model.strip()
        if not normalized or normalized not in self.list_models():
            raise ValueError("Selecione um modelo instalado no Ollama.")
        if self._run("show", normalized).returncode != 0:
            raise RuntimeError(f"O modelo {normalized} não respondeu à verificação do Ollama.")

        settings = self._config_repository.load()
        updated_ai = replace(settings.ai, provider="ollama", model=normalized)
        self._config_repository.save(replace(settings, ai=updated_ai))
        self._model = normalized

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

    def _configured_model(self) -> str:
        try:
            if self._config_repository.exists():
                return self._config_repository.load().ai.model
        except (OSError, ValueError):
            pass
        return DEFAULT_MODEL

    @staticmethod
    def _parse_models(output: str) -> tuple[str, ...]:
        models: list[str] = []
        for line in output.splitlines()[1:]:
            columns = line.split()
            if columns and columns[0] not in models:
                models.append(columns[0])
        return tuple(models)
