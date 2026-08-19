from __future__ import annotations

from pathlib import Path

from ubuntu_ai.remote.models import RemoteHost, RemoteHostKind
from ubuntu_ai.remote.registry import RemoteHostRegistry


def default_inventory_path() -> Path:
    return Path.home() / ".config" / "ubuntu-ai" / "remote-hosts.json"


class RemoteInventoryService:
    """API de aplicação para administrar somente destinos autorizados."""

    def __init__(self, registry: RemoteHostRegistry) -> None:
        self._registry = registry

    def register_ssh(
        self,
        *,
        name: str,
        hostname: str,
        user: str | None = None,
        port: int = 22,
        identity_file: str | None = None,
        known_hosts_file: str | None = None,
        connect_timeout: float = 10.0,
    ) -> RemoteHost:
        host = RemoteHost(
            name=name,
            kind=RemoteHostKind.SSH,
            hostname=hostname,
            user=user,
            port=port,
            identity_file=identity_file,
            known_hosts_file=known_hosts_file,
            connect_timeout=connect_timeout,
        )
        self._registry.register(host)
        return host

    def update_ssh(self, name: str, **changes: object) -> RemoteHost:
        current = self._registry.get(name)
        if current.kind is not RemoteHostKind.SSH:
            raise ValueError("Somente hosts SSH podem ser editados por esta operação.")
        allowed = {
            "hostname",
            "user",
            "port",
            "identity_file",
            "known_hosts_file",
            "connect_timeout",
        }
        unknown = set(changes) - allowed
        if unknown:
            raise ValueError(f"Campos não permitidos: {', '.join(sorted(unknown))}")
        values = {
            "name": current.name,
            "kind": current.kind,
            "hostname": current.hostname,
            "user": current.user,
            "port": current.port,
            "identity_file": current.identity_file,
            "known_hosts_file": current.known_hosts_file,
            "connect_timeout": current.connect_timeout,
        }
        values.update(changes)
        updated = RemoteHost(**values)  # type: ignore[arg-type]
        self._registry.register(updated, replace=True)
        return updated

    def remove(self, name: str) -> RemoteHost:
        return self._registry.remove(name)

    def get(self, name: str) -> RemoteHost:
        return self._registry.get(name)

    def list_hosts(self) -> tuple[RemoteHost, ...]:
        return tuple(host for host in self._registry.all() if host.kind is RemoteHostKind.SSH)
