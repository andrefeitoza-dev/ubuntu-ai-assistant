from __future__ import annotations

from threading import Event


class RemoteCancellationToken:
    """Sinal cooperativo e thread-safe para interromper uma execução remota."""

    def __init__(self) -> None:
        self._event = Event()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> None:
        self._event.set()


class RemoteExecutionCancelled(RuntimeError):
    """Indica que a execução foi interrompida pelo usuário."""
