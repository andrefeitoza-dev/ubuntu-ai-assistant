from __future__ import annotations

import subprocess
import time
from collections.abc import Sequence
from dataclasses import dataclass

from ubuntu_ai.remote.cancellation import (
    RemoteCancellationToken,
    RemoteExecutionCancelled,
)


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
        cancellation: RemoteCancellationToken | None = None,
    ) -> ProcessResult:
        process = subprocess.Popen(
            list(argv),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.monotonic() + timeout

        while True:
            if cancellation is not None and cancellation.cancelled:
                process.terminate()
                try:
                    process.communicate(timeout=1.0)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                raise RemoteExecutionCancelled("Execução remota cancelada pelo usuário.")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                process.kill()
                process.communicate()
                raise TimeoutError(f"Execução excedeu o limite de {timeout:g} segundos.")
            try:
                stdout, stderr = process.communicate(timeout=min(0.05, remaining))
                break
            except subprocess.TimeoutExpired:
                time.sleep(0.01)
        return ProcessResult(
            return_code=process.returncode,
            stdout=stdout,
            stderr=stderr,
        )
