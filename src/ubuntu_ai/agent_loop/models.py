from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from ubuntu_ai.agent.models import AgentResult
from ubuntu_ai.execution.models import ExecutionResult


class LoopState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    WAITING_CONFIRMATION = "waiting_confirmation"
    EXECUTING = "executing"
    REPLANNING = "replanning"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StopReason(Enum):
    GOAL_REACHED = "goal_reached"
    USER_CANCELLED = "user_cancelled"
    EXECUTION_BLOCKED = "execution_blocked"
    MAX_ITERATIONS = "max_iterations"
    NO_PROGRESS = "no_progress"
    PLANNING_ERROR = "planning_error"


@dataclass(slots=True, frozen=True)
class AgentLoopConfig:
    max_iterations: int = 5
    max_stalled_iterations: int = 2

    def __post_init__(self) -> None:
        if self.max_iterations < 1:
            raise ValueError("max_iterations deve ser maior que zero.")
        if self.max_stalled_iterations < 1:
            raise ValueError("max_stalled_iterations deve ser maior que zero.")


@dataclass(slots=True, frozen=True)
class LoopEvent:
    iteration: int
    state: LoopState
    message: str


@dataclass(slots=True, frozen=True)
class IterationRecord:
    number: int
    request: str
    plan_result: AgentResult
    execution_results: tuple[ExecutionResult, ...] = field(default_factory=tuple)

    @property
    def succeeded(self) -> bool:
        return bool(self.execution_results) and all(
            result.status.value in {"approved", "executed"}
            for result in self.execution_results
        )


@dataclass(slots=True, frozen=True)
class LoopSnapshot:
    goal: str
    state: LoopState
    iteration: int
    pending_plan: AgentResult | None
    records: tuple[IterationRecord, ...]
    events: tuple[LoopEvent, ...]
    stop_reason: StopReason | None = None

    @property
    def requires_confirmation(self) -> bool:
        return self.state is LoopState.WAITING_CONFIRMATION
