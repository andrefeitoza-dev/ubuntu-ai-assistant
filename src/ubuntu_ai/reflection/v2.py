from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ubuntu_ai.reflection.critique import SelfCritic, SelfCritique
from ubuntu_ai.reflection.failure import FailureAnalysis, FailureClassifier
from ubuntu_ai.reflection.recovery import RecoveryPlan, RecoveryPlanner
from ubuntu_ai.reflection.root_cause import RootCause, RootCauseAnalyzer


@dataclass(frozen=True, slots=True)
class ReflectionV2Report:
    """Relatório completo de reflexão pós-execução."""

    failure: FailureAnalysis
    root_cause: RootCause
    recovery: RecoveryPlan
    critique: SelfCritique

    @property
    def retry_allowed(self) -> bool:
        return self.recovery.retry_allowed and self.critique.approved

    def summary(self) -> str:
        return (
            f"{self.failure.summary} "
            f"Causa: {self.root_cause.title}. "
            f"Crítica: {self.critique.summary()}"
        )


class ReflectionEngineV2:
    """Pipeline determinístico de reflexão e recuperação."""

    def __init__(
        self,
        classifier: FailureClassifier | None = None,
        root_cause_analyzer: RootCauseAnalyzer | None = None,
        recovery_planner: RecoveryPlanner | None = None,
        critic: SelfCritic | None = None,
    ) -> None:
        self._classifier = classifier or FailureClassifier()
        self._root_cause_analyzer = root_cause_analyzer or RootCauseAnalyzer()
        self._recovery_planner = recovery_planner or RecoveryPlanner()
        self._critic = critic or SelfCritic()

    def reflect(
        self,
        *,
        success: bool,
        message: str = "",
        stdout: str = "",
        stderr: str = "",
    ) -> ReflectionV2Report:
        failure = self._classifier.classify(
            success=success,
            message=message,
            stdout=stdout,
            stderr=stderr,
        )
        root_cause = self._root_cause_analyzer.analyze(failure)
        recovery = self._recovery_planner.build(failure)
        critique = self._critic.evaluate(
            failure=failure,
            root_cause=root_cause,
            recovery=recovery,
        )

        return ReflectionV2Report(
            failure=failure,
            root_cause=root_cause,
            recovery=recovery,
            critique=critique,
        )

    def reflect_execution_result(self, result: Any) -> ReflectionV2Report:
        """Adapta objetos de execução existentes sem acoplar ao modelo concreto."""

        status = getattr(result, "status", None)
        status_value = getattr(status, "value", status)
        success = str(status_value).lower() in {
            "executed",
            "approved",
            "success",
            "succeeded",
        }

        return self.reflect(
            success=success,
            message=str(getattr(result, "message", "") or ""),
            stdout=str(getattr(result, "stdout", "") or ""),
            stderr=str(getattr(result, "stderr", "") or ""),
        )
