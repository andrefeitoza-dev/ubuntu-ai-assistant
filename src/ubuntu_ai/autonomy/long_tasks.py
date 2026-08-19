from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import StrEnum
from threading import RLock
from time import monotonic

from ubuntu_ai.autonomy.control import TaskControl


class LongTaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


_TERMINAL = {
    LongTaskStatus.COMPLETED,
    LongTaskStatus.FAILED,
    LongTaskStatus.CANCELLED,
    LongTaskStatus.TIMED_OUT,
}


@dataclass(frozen=True, slots=True)
class LongTask:
    task_id: str
    goal_id: str
    description: str
    total_steps: int
    max_duration: float = 3600.0
    status: LongTaskStatus = LongTaskStatus.PENDING
    completed_steps: int = 0
    message: str = "Aguardando execução."
    started_at: float | None = None
    updated_at: float | None = None

    def __post_init__(self) -> None:
        if not self.task_id.strip() or not self.goal_id.strip():
            raise ValueError("task_id e goal_id não podem estar vazios.")
        if not self.description.strip():
            raise ValueError("A descrição da tarefa não pode estar vazia.")
        if self.total_steps < 1:
            raise ValueError("total_steps deve ser maior que zero.")
        if not 0 < self.max_duration <= 86_400:
            raise ValueError("max_duration deve estar entre 0 e 86400 segundos.")
        if not 0 <= self.completed_steps <= self.total_steps:
            raise ValueError("Progresso da tarefa inválido.")

    @property
    def progress(self) -> float:
        return self.completed_steps / self.total_steps

    @property
    def terminal(self) -> bool:
        return self.status in _TERMINAL


TaskObserver = Callable[[LongTask], None]


class LongTaskManager:
    """Gerencia tarefas longas com limites e progresso observável."""

    def __init__(self, *, clock: Callable[[], float] = monotonic) -> None:
        self._clock = clock
        self._tasks: dict[str, LongTask] = {}
        self._controls: dict[str, TaskControl] = {}
        self._observers: list[TaskObserver] = []
        self._lock = RLock()

    def register(self, task: LongTask) -> LongTask:
        with self._lock:
            if task.task_id in self._tasks:
                raise ValueError(f"Tarefa já registrada: {task.task_id}")
            self._tasks[task.task_id] = task
            self._controls[task.task_id] = TaskControl()
        self._notify(task)
        return task

    def subscribe(self, observer: TaskObserver) -> None:
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)

    def get(self, task_id: str) -> LongTask:
        with self._lock:
            try:
                return self._tasks[task_id]
            except KeyError as exc:
                raise KeyError(f"Tarefa não encontrada: {task_id}") from exc

    def control(self, task_id: str) -> TaskControl:
        self.get(task_id)
        return self._controls[task_id]

    def all(self) -> tuple[LongTask, ...]:
        with self._lock:
            return tuple(self._tasks.values())

    def active(self) -> tuple[LongTask, ...]:
        return tuple(task for task in self.all() if not task.terminal)

    def start(self, task_id: str, message: str = "Tarefa iniciada.") -> LongTask:
        task = self.get(task_id)
        if task.status is not LongTaskStatus.PENDING:
            raise ValueError("Somente tarefas pendentes podem ser iniciadas.")
        now = self._clock()
        return self._store(
            replace(
                task,
                status=LongTaskStatus.RUNNING,
                message=message,
                started_at=now,
                updated_at=now,
            )
        )

    def advance(
        self,
        task_id: str,
        *,
        completed_steps: int,
        message: str,
    ) -> LongTask:
        task = self._check_running(task_id)
        if completed_steps < task.completed_steps:
            raise ValueError("O progresso não pode retroceder.")
        if completed_steps > task.total_steps:
            raise ValueError("O progresso excede o total de etapas.")

        status = (
            LongTaskStatus.COMPLETED
            if completed_steps == task.total_steps
            else LongTaskStatus.RUNNING
        )
        return self._store(
            replace(
                task,
                completed_steps=completed_steps,
                status=status,
                message=message,
                updated_at=self._clock(),
            )
        )

    def pause(self, task_id: str) -> LongTask:
        task = self._check_running(task_id)
        self.control(task_id).pause()
        return self._store(
            replace(
                task,
                status=LongTaskStatus.PAUSED,
                message="Tarefa pausada.",
                updated_at=self._clock(),
            )
        )

    def resume(self, task_id: str) -> LongTask:
        task = self.get(task_id)
        if task.status is not LongTaskStatus.PAUSED:
            raise ValueError("Somente tarefas pausadas podem ser retomadas.")
        self.control(task_id).resume()
        return self._store(
            replace(
                task,
                status=LongTaskStatus.RUNNING,
                message="Tarefa retomada.",
                updated_at=self._clock(),
            )
        )

    def cancel(self, task_id: str) -> LongTask:
        task = self.get(task_id)
        if task.terminal:
            return task
        self.control(task_id).cancel()
        return self._store(
            replace(
                task,
                status=LongTaskStatus.CANCELLED,
                message="Tarefa cancelada pelo usuário.",
                updated_at=self._clock(),
            )
        )

    def fail(self, task_id: str, reason: str) -> LongTask:
        task = self.get(task_id)
        if task.terminal:
            return task
        return self._store(
            replace(
                task,
                status=LongTaskStatus.FAILED,
                message=reason,
                updated_at=self._clock(),
            )
        )

    def enforce_limits(self, task_id: str) -> LongTask:
        task = self.get(task_id)
        if task.terminal or task.started_at is None:
            return task
        if self._clock() - task.started_at <= task.max_duration:
            return task
        self.control(task_id).cancel()
        return self._store(
            replace(
                task,
                status=LongTaskStatus.TIMED_OUT,
                message="Tempo máximo da tarefa atingido.",
                updated_at=self._clock(),
            )
        )

    def _check_running(self, task_id: str) -> LongTask:
        task = self.enforce_limits(task_id)
        if task.status is not LongTaskStatus.RUNNING:
            raise ValueError("A tarefa não está em execução.")
        self.control(task_id).checkpoint()
        return task

    def _store(self, task: LongTask) -> LongTask:
        with self._lock:
            self._tasks[task.task_id] = task
        self._notify(task)
        return task

    def _notify(self, task: LongTask) -> None:
        with self._lock:
            observers = tuple(self._observers)
        for observer in observers:
            observer(task)
