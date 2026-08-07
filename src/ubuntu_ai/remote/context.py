from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.remote.models import RemoteHost


@dataclass(frozen=True, slots=True)
class RemoteContext:
    """Contexto mínimo associado a um host remoto."""

    host_name: str
    hostname: str | None
    user: str | None
    kind: str


class RemoteContextBuilder:
    def build(self, host: RemoteHost) -> RemoteContext:
        return RemoteContext(
            host_name=host.name,
            hostname=host.hostname,
            user=host.user,
            kind=host.kind.value,
        )
