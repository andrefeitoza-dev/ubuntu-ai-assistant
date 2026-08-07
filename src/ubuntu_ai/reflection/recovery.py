from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ubuntu_ai.reflection.failure import FailureAnalysis, FailureKind


class RecoveryAction(StrEnum):
    RETRY = "retry"
    VERIFY_PERMISSIONS = "verify_permissions"
    VERIFY_RESOURCE = "verify_resource"
    VERIFY_NETWORK = "verify_network"
    INSTALL_DEPENDENCY = "install_dependency"
    CORRECT_INPUT = "correct_input"
    REQUIRE_REVIEW = "require_review"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class RecoveryPlan:
    """Estratégia de recuperação sem executar alterações automaticamente."""

    actions: tuple[RecoveryAction, ...]
    retry_allowed: bool
    requires_confirmation: bool
    guidance: tuple[str, ...] = ()


class RecoveryPlanner:
    """Deriva uma estratégia segura de recuperação."""

    def build(self, failure: FailureAnalysis) -> RecoveryPlan:
        if failure.kind is FailureKind.NONE:
            return RecoveryPlan(
                actions=(RecoveryAction.NONE,),
                retry_allowed=False,
                requires_confirmation=False,
            )

        if failure.kind is FailureKind.PERMISSION:
            return RecoveryPlan(
                actions=(
                    RecoveryAction.VERIFY_PERMISSIONS,
                    RecoveryAction.REQUIRE_REVIEW,
                ),
                retry_allowed=False,
                requires_confirmation=True,
                guidance=(
                    "Verifique proprietário, grupo e permissões antes de elevar privilégios.",
                ),
            )

        if failure.kind is FailureKind.NOT_FOUND:
            return RecoveryPlan(
                actions=(RecoveryAction.VERIFY_RESOURCE,),
                retry_allowed=True,
                requires_confirmation=False,
                guidance=(
                    "Confirme a existência do comando, arquivo ou recurso antes de repetir.",
                ),
            )

        if failure.kind is FailureKind.NETWORK:
            return RecoveryPlan(
                actions=(
                    RecoveryAction.VERIFY_NETWORK,
                    RecoveryAction.RETRY,
                ),
                retry_allowed=True,
                requires_confirmation=False,
                guidance=(
                    "Valide conectividade e resolução DNS antes da nova tentativa.",
                ),
            )

        if failure.kind is FailureKind.DEPENDENCY:
            return RecoveryPlan(
                actions=(
                    RecoveryAction.INSTALL_DEPENDENCY,
                    RecoveryAction.REQUIRE_REVIEW,
                ),
                retry_allowed=False,
                requires_confirmation=True,
                guidance=(
                    "Identifique a dependência exata antes de instalar ou atualizar pacotes.",
                ),
            )

        if failure.kind is FailureKind.TIMEOUT:
            return RecoveryPlan(
                actions=(RecoveryAction.RETRY,),
                retry_allowed=True,
                requires_confirmation=False,
                guidance=(
                    "Repita apenas se o estado atual do sistema indicar que a operação é segura.",
                ),
            )

        if failure.kind is FailureKind.INVALID_INPUT:
            return RecoveryPlan(
                actions=(RecoveryAction.CORRECT_INPUT,),
                retry_allowed=False,
                requires_confirmation=False,
                guidance=(
                    "Corrija os argumentos antes de qualquer nova execução.",
                ),
            )

        return RecoveryPlan(
            actions=(RecoveryAction.REQUIRE_REVIEW,),
            retry_allowed=False,
            requires_confirmation=True,
            guidance=(
                "A falha não é conhecida; faça revisão manual antes de continuar.",
            ),
        )
