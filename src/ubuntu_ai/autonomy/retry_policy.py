from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.autonomy.goal import Goal
from ubuntu_ai.reflection.v2 import ReflectionV2Report


@dataclass(frozen=True, slots=True)
class RetryDecision:
    retry: bool
    reason: str


class RetryPolicy:
    """Decide se o loop deve tentar novamente."""

    def evaluate(
        self,
        goal: Goal,
        reflection: ReflectionV2Report | None,
    ) -> RetryDecision:
        if goal.attempts >= goal.max_attempts:
            return RetryDecision(
                retry=False,
                reason="Limite de tentativas atingido.",
            )

        if reflection is None:
            return RetryDecision(
                retry=False,
                reason="Sem reflexão disponível.",
            )

        if reflection.retry_allowed:
            return RetryDecision(
                retry=True,
                reason="Reflection V2 autorizou nova tentativa.",
            )

        return RetryDecision(
            retry=False,
            reason="Reflection V2 não autorizou retry.",
        )
