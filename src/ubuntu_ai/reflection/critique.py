from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.reflection.failure import FailureAnalysis
from ubuntu_ai.reflection.recovery import RecoveryPlan
from ubuntu_ai.reflection.root_cause import RootCause


@dataclass(frozen=True, slots=True)
class SelfCritique:
    """Autoavaliação estruturada sobre uma execução."""

    score: float
    confidence: float
    approved: bool
    findings: tuple[str, ...] = ()

    def summary(self) -> str:
        if not self.findings:
            return "Nenhum problema relevante identificado."
        return " | ".join(self.findings)


class SelfCritic:
    """Calcula uma crítica determinística a partir da reflexão."""

    def evaluate(
        self,
        *,
        failure: FailureAnalysis,
        root_cause: RootCause,
        recovery: RecoveryPlan,
    ) -> SelfCritique:
        if not failure.failed:
            return SelfCritique(
                score=1.0,
                confidence=1.0,
                approved=True,
            )

        findings = [
            failure.summary,
            f"Causa provável: {root_cause.title}.",
        ]

        if recovery.requires_confirmation:
            findings.append("A recuperação exige confirmação.")

        if failure.confidence < 0.5:
            findings.append("A classificação da falha possui baixa confiança.")

        score = max(0.0, 1.0 - failure.confidence)
        approved = (
            recovery.retry_allowed
            and not recovery.requires_confirmation
            and failure.confidence >= 0.5
        )

        return SelfCritique(
            score=round(score, 2),
            confidence=failure.confidence,
            approved=approved,
            findings=tuple(findings),
        )
