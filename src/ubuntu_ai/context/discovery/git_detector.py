from __future__ import annotations

import subprocess
from pathlib import Path


class GitDetector:
    """Detecta informações do repositório Git."""

    def is_repository(
        self,
        working_directory: str,
    ) -> bool:
        return (Path(working_directory) / ".git").exists()

    def branch(
        self,
        working_directory: str,
    ) -> str | None:
        if not self.is_repository(working_directory):
            return None

        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=working_directory,
                capture_output=True,
                text=True,
                check=False,
            )

            branch = result.stdout.strip()

            return branch or None

        except OSError:
            return None