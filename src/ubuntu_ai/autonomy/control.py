from __future__ import annotations

from threading import Condition, Event


class TaskCancelledError(RuntimeError):
    """Interrompe cooperativamente uma tarefa longa."""


class TaskControl:
    """Controle thread-safe de pausa, retomada e cancelamento cooperativo."""

    def __init__(self) -> None:
        self._cancelled = Event()
        self._condition = Condition()
        self._paused = False

    @property
    def cancelled(self) -> bool:
        return self._cancelled.is_set()

    @property
    def paused(self) -> bool:
        with self._condition:
            return self._paused

    def pause(self) -> None:
        with self._condition:
            if not self._cancelled.is_set():
                self._paused = True

    def resume(self) -> None:
        with self._condition:
            self._paused = False
            self._condition.notify_all()

    def cancel(self) -> None:
        self._cancelled.set()
        with self._condition:
            self._paused = False
            self._condition.notify_all()

    def checkpoint(self) -> None:
        """Bloqueia durante pausa e levanta exceção após cancelamento."""

        with self._condition:
            while self._paused and not self._cancelled.is_set():
                self._condition.wait()

        if self._cancelled.is_set():
            raise TaskCancelledError("Tarefa cancelada pelo usuário.")
