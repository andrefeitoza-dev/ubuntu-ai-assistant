from __future__ import annotations

from hashlib import sha256

from ubuntu_ai.execution.models import ExecutionResult


class LoopWatchdog:
    """Detecta repetição de resultados e ausência de progresso."""

    def __init__(self, max_stalled_iterations: int = 2) -> None:
        if max_stalled_iterations < 1:
            raise ValueError("max_stalled_iterations deve ser maior que zero.")
        self._max_stalled_iterations = max_stalled_iterations
        self._last_signature: str | None = None
        self._stalled = 0

    @property
    def stalled_iterations(self) -> int:
        return self._stalled

    def observe(self, results: tuple[ExecutionResult, ...]) -> bool:
        signature = self._signature(results)
        if signature == self._last_signature:
            self._stalled += 1
        else:
            self._last_signature = signature
            self._stalled = 0
        return self._stalled >= self._max_stalled_iterations

    def reset(self) -> None:
        self._last_signature = None
        self._stalled = 0

    @staticmethod
    def _signature(results: tuple[ExecutionResult, ...]) -> str:
        payload = "\n".join(
            "|".join(
                (
                    result.status.value,
                    result.command or "",
                    str(result.return_code),
                    result.stdout.strip(),
                    result.stderr.strip(),
                    result.message.strip(),
                )
            )
            for result in results
        )
        return sha256(payload.encode("utf-8")).hexdigest()
