from __future__ import annotations

import subprocess
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProcessResult:
    return_code: int
    stdout: str
    stderr: str


class ProcessRunner:
    """Fronteira substituível para execução de processos."""

    def run(
        self,
        argv: Sequence[str],
        *,
        timeout: float,
    ) -> ProcessResult:
        completed = subprocess.run(
            list(argv),
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        return ProcessResult(
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
