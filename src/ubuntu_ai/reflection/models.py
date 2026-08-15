from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ReflectionSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ReflectionPhase(Enum):
    PLAN = "plan"
    EXECUTION = "execution"


@dataclass(slots=True, frozen=True)
class ReflectionFinding:
    code: str
    message: str
    severity: ReflectionSeverity = ReflectionSeverity.INFO
    step_index: int | None = None
    recommendation: str | None = None


@dataclass(slots=True, frozen=True)
class ReflectionReport:
    phase: ReflectionPhase
    findings: tuple[ReflectionFinding, ...] = field(default_factory=tuple)
    score: float = 1.0

    @property
    def has_critical_findings(self) -> bool:
        return any(finding.severity is ReflectionSeverity.CRITICAL for finding in self.findings)

    @property
    def approved(self) -> bool:
        return not self.has_critical_findings

    def summary(self) -> str:
        if not self.findings:
            return "Reflexão concluída sem observações."
        labels = {
            ReflectionSeverity.INFO: "INFO",
            ReflectionSeverity.WARNING: "AVISO",
            ReflectionSeverity.CRITICAL: "CRÍTICO",
        }
        return "\n".join(
            f"[{labels[item.severity]}] {item.message}"
            + (f" Recomendação: {item.recommendation}" if item.recommendation else "")
            for item in self.findings
        )
