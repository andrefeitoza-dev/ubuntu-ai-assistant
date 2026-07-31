from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CheckSeverity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass(slots=True, frozen=True)
class ToolEnvironment:
    name: str
    executable: str
    available: bool
    path: str | None = None
    version: str | None = None


@dataclass(slots=True, frozen=True)
class PreflightCheck:
    code: str
    message: str
    passed: bool
    severity: CheckSeverity = CheckSeverity.ERROR
    recommendation: str | None = None


@dataclass(slots=True, frozen=True)
class PreflightReport:
    tool_name: str
    checks: tuple[PreflightCheck, ...]

    @property
    def ready(self) -> bool:
        return all(
            check.passed or check.severity is not CheckSeverity.ERROR
            for check in self.checks
        )

    @property
    def errors(self) -> tuple[PreflightCheck, ...]:
        return tuple(
            check
            for check in self.checks
            if not check.passed and check.severity is CheckSeverity.ERROR
        )

    def summary(self) -> str:
        if self.ready:
            return f"Preflight aprovado para {self.tool_name}."
        details = "; ".join(check.message for check in self.errors)
        return f"Preflight reprovado para {self.tool_name}: {details}"
