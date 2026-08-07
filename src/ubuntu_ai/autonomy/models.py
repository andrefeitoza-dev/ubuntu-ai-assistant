from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.autonomy.goal import Goal
from ubuntu_ai.runtime_integration.models import RuntimeCycleResult


@dataclass(frozen=True, slots=True)
class AutonomousCycleResult:
    goal: Goal
    runtime_result: RuntimeCycleResult | None
    completed: bool
    retry_scheduled: bool
    reason: str
