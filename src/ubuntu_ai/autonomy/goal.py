from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum


class GoalStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Goal:
    goal_id: str
    description: str
    status: GoalStatus = GoalStatus.PENDING
    progress: float = 0.0
    attempts: int = 0
    max_attempts: int = 3

    def __post_init__(self) -> None:
        if not self.goal_id.strip():
            raise ValueError("goal_id não pode estar vazio.")
        if not self.description.strip():
            raise ValueError("A descrição do objetivo não pode estar vazia.")
        if self.max_attempts < 1:
            raise ValueError("max_attempts deve ser maior que zero.")
        if not 0.0 <= self.progress <= 1.0:
            raise ValueError("progress deve estar entre 0 e 1.")

    def with_status(self, status: GoalStatus) -> Goal:
        return replace(self, status=status)

    def with_progress(self, progress: float) -> Goal:
        return replace(
            self,
            progress=max(0.0, min(progress, 1.0)),
        )

    def increment_attempts(self) -> Goal:
        return replace(self, attempts=self.attempts + 1)
