from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.reflection.failure import FailureKind
from ubuntu_ai.reflection.v2 import ReflectionV2Report


@dataclass(frozen=True, slots=True)
class HealingAdvice:
    action: str
    safe_to_automate: bool
    reason: str


class SelfHealingAdvisor:
    """Traduz a reflexão em uma recomendação de recuperação."""

    def advise(
        self,
        reflection: ReflectionV2Report,
    ) -> HealingAdvice:
        kind = reflection.failure.kind

        if kind is FailureKind.NETWORK and reflection.retry_allowed:
            return HealingAdvice(
                action="retry",
                safe_to_automate=True,
                reason="Falha transitória de rede com retry autorizado.",
            )

        if kind is FailureKind.TIMEOUT and reflection.retry_allowed:
            return HealingAdvice(
                action="retry",
                safe_to_automate=True,
                reason="Timeout recuperável.",
            )

        if kind is FailureKind.NOT_FOUND:
            return HealingAdvice(
                action="verify_resource",
                safe_to_automate=False,
                reason="Recurso ausente exige validação.",
            )

        return HealingAdvice(
            action="review",
            safe_to_automate=False,
            reason="Recuperação automática não é segura.",
        )
