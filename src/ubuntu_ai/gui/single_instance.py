"""Coordena uma única instância da interface gráfica."""

from __future__ import annotations

import fcntl
import os
import signal
import tempfile
from collections.abc import Callable
from pathlib import Path
from types import FrameType

APP_LOCK_NAME = "ubuntu-ai-assistant.lock"


def default_lock_path() -> Path:
    """Retorna uma trava por usuário, preferindo o runtime da sessão gráfica."""

    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if runtime:
        return Path(runtime) / APP_LOCK_NAME

    directory = Path(tempfile.gettempdir()) / f"ubuntu-ai-{os.getuid()}"
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    directory.chmod(0o700)
    return directory / APP_LOCK_NAME


class SingleInstance:
    """Ativa a janela existente quando uma segunda instância é solicitada."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or default_lock_path()
        self._file_descriptor: int | None = None
        self._previous_handler: signal.Handlers | None = None
        self._owns_lock = False
        self._activate: Callable[[], None] | None = None
        self._pending_activation = False

    def acquire_or_activate(self) -> bool:
        """Adquire a trava ou pede que a instância existente seja exibida."""

        self.path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        descriptor = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        os.chmod(self.path, 0o600)

        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            activated = self._activate_existing(descriptor)
            os.close(descriptor)
            if activated:
                return False
            raise RuntimeError("A instância existente não pôde ser ativada.") from None

        os.ftruncate(descriptor, 0)
        os.write(descriptor, f"{os.getpid()}\n".encode())
        os.fsync(descriptor)
        self._file_descriptor = descriptor
        self._owns_lock = True
        self._previous_handler = signal.signal(signal.SIGUSR1, self._handle_activation)
        return True

    def start(self, activate: Callable[[], None]) -> None:
        """Registra a ativação da janela na thread principal da aplicação."""

        if not self._owns_lock:
            raise RuntimeError("A instância deve adquirir a trava antes de iniciar.")

        self._activate = activate
        if self._pending_activation:
            self._pending_activation = False
            activate()

    def close(self) -> None:
        """Libera a trava pertencente à instância atual."""

        if self._previous_handler is not None:
            signal.signal(signal.SIGUSR1, self._previous_handler)
            self._previous_handler = None
        self._activate = None

        if self._file_descriptor is not None:
            fcntl.flock(self._file_descriptor, fcntl.LOCK_UN)
            os.close(self._file_descriptor)
            self._file_descriptor = None

        if self._owns_lock:
            self.path.unlink(missing_ok=True)
            self._owns_lock = False

    @staticmethod
    def _activate_existing(descriptor: int) -> bool:
        os.lseek(descriptor, 0, os.SEEK_SET)
        value = os.read(descriptor, 32).decode(errors="ignore").strip()
        try:
            process_id = int(value)
        except ValueError:
            return False

        try:
            os.kill(process_id, signal.SIGUSR1)
        except (ProcessLookupError, PermissionError):
            return False
        return True

    def _handle_activation(self, _signum: int, _frame: FrameType | None) -> None:
        if self._activate is None:
            self._pending_activation = True
            return
        self._activate()
