from __future__ import annotations

import shutil


class OllamaDetector:
    """Detecta se o Ollama está instalado."""

    def available(self) -> bool:
        return shutil.which("ollama") is not None
