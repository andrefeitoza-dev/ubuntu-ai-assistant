from __future__ import annotations

from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AutonomousTask:
    task_id: str
    goal_id: str
    payload: object
    priority: int = 100


class TaskQueue:
    """Fila priorizada simples para tarefas autônomas."""

    def __init__(self) -> None:
        self._items: deque[AutonomousTask] = deque()

    def push(self, task: AutonomousTask) -> None:
        self._items.append(task)
        self._items = deque(
            sorted(
                self._items,
                key=lambda item: item.priority,
                reverse=True,
            )
        )

    def pop(self) -> AutonomousTask | None:
        if not self._items:
            return None
        return self._items.popleft()

    def __len__(self) -> int:
        return len(self._items)
