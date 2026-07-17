from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(Enum):
    """Representa o resultado da tentativa de execução."""

    APPROVED = "approved"
    BLOCKED = "blocked"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass(slots=True, frozen=True)
class ExecutionRequest:
    """Solicitação de execução validada pelo pipeline."""

    command: str
    dry_run: bool = False


@dataclass(slots=True, frozen=True)
class ExecutionResult:
    """Resultado produzido por uma execução."""

    status: ExecutionStatus
    message: str