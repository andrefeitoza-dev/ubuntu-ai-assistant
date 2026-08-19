from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.remote.engine import RemoteExecutionEngine
from ubuntu_ai.remote.models import RemoteCommand, RemoteExecutionResult


@dataclass(frozen=True, slots=True)
class RemoteDiagnosticItem:
    name: str
    command: tuple[str, ...]
    output: str
    success: bool


@dataclass(frozen=True, slots=True)
class RemoteSystemContext:
    host_name: str
    items: tuple[RemoteDiagnosticItem, ...]

    def get(self, name: str) -> RemoteDiagnosticItem:
        for item in self.items:
            if item.name == name:
                return item
        raise KeyError(name)


class RemoteDiagnosticService:
    """Coleta contexto Ubuntu somente com consultas de leitura."""

    _COMMANDS = (
        ("system", ("uname", "-srmo")),
        ("cpu", ("nproc",)),
        ("memory", ("free", "-m")),
        ("disk", ("df", "-h", "/")),
        ("network", ("ip", "-brief", "address")),
        ("services", ("systemctl", "--failed", "--no-legend")),
    )

    def __init__(self, engine: RemoteExecutionEngine) -> None:
        self._engine = engine

    def collect(self, host_name: str, *, timeout: float = 15.0) -> RemoteSystemContext:
        items = tuple(
            self._item(
                name, command, self._engine.execute(host_name, RemoteCommand(command, timeout))
            )
            for name, command in self._COMMANDS
        )
        return RemoteSystemContext(host_name=host_name, items=items)

    @staticmethod
    def _item(
        name: str,
        command: tuple[str, ...],
        result: RemoteExecutionResult,
    ) -> RemoteDiagnosticItem:
        output = result.stdout.strip() if result.success else result.stderr.strip()
        return RemoteDiagnosticItem(name, command, output, result.success)
