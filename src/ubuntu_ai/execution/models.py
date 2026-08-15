from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(Enum):
    APPROVED = "approved"
    BLOCKED = "blocked"
    EXECUTED = "executed"
    FAILED = "failed"


@dataclass(slots=True, frozen=True)
class ExecutionRequest:
    command: str
    dry_run: bool = False


@dataclass(slots=True, frozen=True)
class ExecutionResult:
    status: ExecutionStatus
    message: str
    command: str | None = None
    return_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration: float | None = None
