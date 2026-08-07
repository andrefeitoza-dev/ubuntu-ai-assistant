from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.remote.models import RemoteHost, RemoteHostKind


@dataclass(frozen=True, slots=True)
class ConnectionSpec:
    """Especificação de conexão derivada de um host."""

    host: RemoteHost
    address: str

    @property
    def is_remote(self) -> bool:
        return self.host.kind is not RemoteHostKind.LOCAL


class ConnectionResolver:
    """Resolve uma definição de host para uma especificação de conexão."""

    def resolve(self, host: RemoteHost) -> ConnectionSpec:
        if host.kind is RemoteHostKind.LOCAL:
            address = "localhost"
        elif host.kind is RemoteHostKind.SSH:
            address = (
                f"{host.user}@{host.hostname}"
                if host.user
                else str(host.hostname)
            )
        else:
            address = str(host.container)

        return ConnectionSpec(
            host=host,
            address=address,
        )
