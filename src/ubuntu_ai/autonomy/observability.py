from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from datetime import UTC, datetime

from ubuntu_ai.autonomy.long_tasks import LongTask, LongTaskStatus


@dataclass(frozen=True, slots=True)
class AutomationEvent:
    task_id: str
    goal_id: str
    status: LongTaskStatus
    progress: float
    message: str
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class AutomationMetrics:
    total_events: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    cancelled_tasks: int
    timed_out_tasks: int
    average_progress: float


class AutomationTelemetry:
    """Coleta eventos estruturados e métricas sem armazenar payloads."""

    def __init__(self, *, capacity: int = 1000) -> None:
        if capacity < 1 or capacity > 10_000:
            raise ValueError("capacity deve estar entre 1 e 10000.")
        self._events: deque[AutomationEvent] = deque(maxlen=capacity)
        self._latest: dict[str, LongTask] = {}

    def observe(self, task: LongTask) -> None:
        self._latest[task.task_id] = task
        self._events.append(
            AutomationEvent(
                task_id=task.task_id,
                goal_id=task.goal_id,
                status=task.status,
                progress=task.progress,
                message=task.message,
                recorded_at=datetime.now(UTC),
            )
        )

    def events(self, *, task_id: str | None = None) -> tuple[AutomationEvent, ...]:
        return tuple(event for event in self._events if task_id is None or event.task_id == task_id)

    def metrics(self) -> AutomationMetrics:
        tasks = tuple(self._latest.values())
        counts = Counter(task.status for task in tasks)
        active = sum(not task.terminal for task in tasks)
        average = sum(task.progress for task in tasks) / len(tasks) if tasks else 0.0
        return AutomationMetrics(
            total_events=len(self._events),
            active_tasks=active,
            completed_tasks=counts[LongTaskStatus.COMPLETED],
            failed_tasks=counts[LongTaskStatus.FAILED],
            cancelled_tasks=counts[LongTaskStatus.CANCELLED],
            timed_out_tasks=counts[LongTaskStatus.TIMED_OUT],
            average_progress=average,
        )
