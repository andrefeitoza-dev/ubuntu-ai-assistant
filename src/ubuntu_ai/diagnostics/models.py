from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class DiagnosticStatus(StrEnum):
    """Estados possíveis de uma verificação diagnóstica."""

    PASSED = "passed"
    WARNING = "warning"
    FAILED = "failed"


@dataclass(slots=True, frozen=True)
class DiagnosticCheck:
    """Resultado de uma etapa do diagnóstico de IA."""

    name: str
    status: DiagnosticStatus
    message: str
    duration_seconds: float | None = None
    details: dict[str, str] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class AIDiagnosticReport:
    """Relatório completo do diagnóstico do runtime de IA."""

    provider: str
    model: str
    checks: tuple[DiagnosticCheck, ...]

    @property
    def successful(self) -> bool:
        """Indica se nenhuma verificação terminou com falha."""

        return all(check.status is not DiagnosticStatus.FAILED for check in self.checks)
