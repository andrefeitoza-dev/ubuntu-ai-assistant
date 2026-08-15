from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryDecision:
    retry: bool
    delay_seconds: float
    reason: str


class RetryPolicy:
    """Política conservadora para operações explicitamente idempotentes."""

    _TRANSIENT = (TimeoutError, ConnectionError)

    def __init__(
        self,
        *,
        max_attempts: int = 3,
        base_delay_seconds: float = 0.25,
        max_delay_seconds: float = 2.0,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts deve ser maior que zero.")
        if base_delay_seconds < 0:
            raise ValueError("base_delay_seconds não pode ser negativo.")
        if max_delay_seconds < base_delay_seconds:
            raise ValueError("max_delay_seconds não pode ser menor que base_delay_seconds.")

        self._max_attempts = max_attempts
        self._base_delay = base_delay_seconds
        self._max_delay = max_delay_seconds

    def evaluate(
        self,
        *,
        error: Exception,
        attempt: int,
        idempotent: bool,
    ) -> RetryDecision:
        if not idempotent:
            return RetryDecision(
                retry=False,
                delay_seconds=0.0,
                reason="Retry bloqueado para operação não idempotente.",
            )

        if attempt >= self._max_attempts:
            return RetryDecision(
                retry=False,
                delay_seconds=0.0,
                reason="Limite de tentativas atingido.",
            )

        if not isinstance(error, self._TRANSIENT):
            return RetryDecision(
                retry=False,
                delay_seconds=0.0,
                reason="Falha não classificada como transitória.",
            )

        delay = min(
            self._max_delay,
            self._base_delay * (2 ** max(0, attempt - 1)),
        )
        return RetryDecision(
            retry=True,
            delay_seconds=delay,
            reason="Falha transitória em operação idempotente.",
        )
