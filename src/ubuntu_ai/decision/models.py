from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ExecutionMode(StrEnum):
    LOCAL = "local"
    CONTAINER = "container"
    REVIEW = "review"


class DecisionStrategy(StrEnum):
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AUTOMATION_FIRST = "automation_first"


@dataclass(frozen=True, slots=True)
class Decision:
    strategy: DecisionStrategy
    execution_mode: ExecutionMode
    preferred_tools: tuple[str, ...] = ()
    preferred_skills: tuple[str, ...] = ()
    risk_hints: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    def to_prompt(self) -> str:
        lines = [
            f"Strategy: {self.strategy.value}",
            f"Execution mode: {self.execution_mode.value}",
        ]
        if self.preferred_tools:
            lines.append("Preferred tools: " + ", ".join(self.preferred_tools))
        if self.preferred_skills:
            lines.append("Preferred skills: " + ", ".join(self.preferred_skills))
        if self.risk_hints:
            lines.append("Risk hints:")
            lines.extend(f"- {item}" for item in self.risk_hints)
        if self.reasons:
            lines.append("Decision reasons:")
            lines.extend(f"- {item}" for item in self.reasons)
        return "\n".join(lines)
