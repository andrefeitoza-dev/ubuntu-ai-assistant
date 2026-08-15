from __future__ import annotations

import shutil


class DockerDetector:
    """Detecta se o Docker está disponível."""

    def available(self) -> bool:
        return shutil.which("docker") is not None
