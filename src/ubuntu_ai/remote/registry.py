from __future__ import annotations

from ubuntu_ai.remote.models import RemoteHost


class RemoteHostRegistry:
    """Catálogo em memória de destinos conhecidos."""

    def __init__(self) -> None:
        self._hosts: dict[str, RemoteHost] = {}

    def register(
        self,
        host: RemoteHost,
        *,
        replace: bool = False,
    ) -> None:
        key = host.name.strip().lower()
        if key in self._hosts and not replace:
            raise ValueError(f"Host já registrado: {host.name}")
        self._hosts[key] = host

    def get(self, name: str) -> RemoteHost:
        key = name.strip().lower()
        try:
            return self._hosts[key]
        except KeyError as exc:
            raise KeyError(f"Host não encontrado: {name}") from exc

    def all(self) -> tuple[RemoteHost, ...]:
        return tuple(self._hosts[key] for key in sorted(self._hosts))
