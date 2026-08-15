from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProgressSnapshot:
    completed_steps: int
    total_steps: int

    @property
    def ratio(self) -> float:
        if self.total_steps <= 0:
            return 0.0
        return min(1.0, self.completed_steps / self.total_steps)


class ProgressTracker:
    def calculate(
        self,
        *,
        completed_steps: int,
        total_steps: int,
    ) -> ProgressSnapshot:
        if completed_steps < 0 or total_steps < 0:
            raise ValueError("Valores de progresso não podem ser negativos.")
        if completed_steps > total_steps:
            completed_steps = total_steps

        return ProgressSnapshot(
            completed_steps=completed_steps,
            total_steps=total_steps,
        )
