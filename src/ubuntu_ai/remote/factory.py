from __future__ import annotations

from pathlib import Path

from ubuntu_ai.remote.audit import RemoteAuditService
from ubuntu_ai.remote.engine import RemoteExecutionEngine
from ubuntu_ai.remote.models import RemoteHost, RemoteHostKind
from ubuntu_ai.remote.registry import RemoteHostRegistry


def build_remote_engine(
    *,
    inventory_path: Path | None = None,
    audit_directory: Path | None = None,
) -> RemoteExecutionEngine:
    """Cria engine com host local padrão."""

    registry = RemoteHostRegistry(inventory_path)
    registry.register(
        RemoteHost(
            name="local",
            kind=RemoteHostKind.LOCAL,
        ),
        replace=True,
    )
    return RemoteExecutionEngine(
        registry,
        audit=(RemoteAuditService(audit_directory) if audit_directory is not None else None),
    )
