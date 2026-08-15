from dataclasses import dataclass, field

from ubuntu_ai.domain.risk import RiskLevel


@dataclass(slots=True, init=False)
class PlanStep:
    title: str
    description: str
    command: list[str] | tuple[str, ...]
    tool_name: str | None = None

    def __init__(
        self,
        title: str = "",
        description: str = "",
        command: list[str] | tuple[str, ...] = (),
        tool_name: str | None = None,
    ) -> None:
        self.title = title
        self.description = description
        self.command = command
        self.tool_name = tool_name


@dataclass(slots=True, init=False)
class Plan:
    goal: str
    estimated_seconds: int
    risk: RiskLevel
    planner: str
    steps: list[PlanStep] | tuple[PlanStep, ...] = field(default_factory=list)

    def __init__(
        self,
        goal: str | None = None,
        estimated_seconds: int = 0,
        risk: RiskLevel = RiskLevel.LOW,
        steps: list[PlanStep] | tuple[PlanStep, ...] | None = None,
        planner: str = "unknown",
        *,
        title: str | None = None,
    ) -> None:
        resolved_goal = goal if goal is not None else title
        if resolved_goal is None:
            raise TypeError("Plan requer 'goal' (ou o alias legado 'title').")

        self.goal = resolved_goal
        self.estimated_seconds = estimated_seconds
        self.risk = risk
        self.planner = planner
        self.steps = [] if steps is None else steps

    @property
    def title(self) -> str:
        """Alias legado para compatibilidade com integrações anteriores."""
        return self.goal

    def add_step(self, step: PlanStep) -> None:
        if isinstance(self.steps, tuple):
            self.steps = list(self.steps)
        self.steps.append(step)
