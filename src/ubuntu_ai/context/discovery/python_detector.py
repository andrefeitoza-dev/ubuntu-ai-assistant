from __future__ import annotations

import os
import platform


class PythonDetector:
    """Detecta informações da instalação atual do Python."""

    def version(self) -> str:
        return platform.python_version()

    def virtual_environment(self) -> str | None:
        return os.environ.get("VIRTUAL_ENV")