from __future__ import annotations

from ubuntu_ai.remote.engine import RemoteExecutionEngine
from ubuntu_ai.remote.models import RemoteHost, RemoteHostKind
from ubuntu_ai.remote.registry import RemoteHostRegistry


def build_remote_engine() -> RemoteExecutionEngine:
    """Cria engine com host local padrão."""

    registry = RemoteHostRegistry()
    registry.register(
        RemoteHost(
            name="local",
            kind=RemoteHostKind.LOCAL,
        )
    )
    return RemoteExecutionEngine(registry)
