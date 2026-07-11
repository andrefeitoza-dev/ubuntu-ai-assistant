from dataclasses import dataclass, field

from ubuntu_ai.domain.risk import RiskLevel


@dataclass(slots=True)
class PlanStep:
    title: str
    description: str
    command: str


@dataclass(slots=True)
class Plan:
    goal: str
    estimated_seconds: int
    risk: RiskLevel
    steps: list[PlanStep] = field(default_factory=list)

    def add_step(self, step: PlanStep) -> None:
        self.steps.append(step)
