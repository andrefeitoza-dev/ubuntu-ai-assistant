from __future__ import annotations

from pathlib import Path


class ProjectDetector:
    """Detecta informações básicas do projeto atual."""

    def detect(
        self,
        working_directory: str,
    ) -> str | None:
        path = Path(working_directory)

        if (path / ".git").exists():
            return path.name

        pyproject = path / "pyproject.toml"

        if pyproject.exists():
            return path.name

        return None
