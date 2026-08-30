from __future__ import annotations

from threading import Lock


class ExecutionMode:
    """Estado de simulação da sessão, seguro para acesso entre threads."""

    def __init__(self) -> None:
        self._simulation = False
        self._lock = Lock()

    @property
    def simulation(self) -> bool:
        with self._lock:
            return self._simulation

    def set_simulation(self, enabled: bool) -> bool:
        with self._lock:
            self._simulation = bool(enabled)
            return self._simulation


execution_mode = ExecutionMode()
