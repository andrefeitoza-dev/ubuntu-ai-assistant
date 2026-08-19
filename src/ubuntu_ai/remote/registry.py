from __future__ import annotations

import json
import os
from pathlib import Path

from ubuntu_ai.remote.models import RemoteHost, RemoteHostKind


class RemoteHostRegistry:
    """Catálogo em memória de destinos conhecidos."""

    def __init__(self, storage_path: Path | None = None) -> None:
        self._hosts: dict[str, RemoteHost] = {}
        self._storage_path = storage_path
        self._load()

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
        self._save()

    def remove(self, name: str) -> RemoteHost:
        key = name.strip().lower()
        try:
            host = self._hosts.pop(key)
        except KeyError as exc:
            raise KeyError(f"Host não encontrado: {name}") from exc
        self._save()
        return host

    def get(self, name: str) -> RemoteHost:
        key = name.strip().lower()
        try:
            return self._hosts[key]
        except KeyError as exc:
            raise KeyError(f"Host não encontrado: {name}") from exc

    def all(self) -> tuple[RemoteHost, ...]:
        return tuple(self._hosts[key] for key in sorted(self._hosts))

    def _load(self) -> None:
        if self._storage_path is None or not self._storage_path.exists():
            return
        try:
            data = json.loads(self._storage_path.read_text(encoding="utf-8"))
            hosts = data.get("hosts", [])
            if not isinstance(hosts, list):
                raise ValueError
            for item in hosts:
                host = RemoteHost(
                    name=item["name"],
                    kind=RemoteHostKind(item["kind"]),
                    hostname=item.get("hostname"),
                    user=item.get("user"),
                    port=item.get("port", 22),
                    container=item.get("container"),
                    identity_file=item.get("identity_file"),
                    known_hosts_file=item.get("known_hosts_file"),
                    connect_timeout=item.get("connect_timeout", 10.0),
                )
                self._hosts[host.name.lower()] = host
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise ValueError("Inventário remoto inválido ou corrompido.") from exc

    def _save(self) -> None:
        if self._storage_path is None:
            return
        self._storage_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        payload = {
            "version": 1,
            "hosts": [
                {
                    "name": host.name,
                    "kind": host.kind.value,
                    "hostname": host.hostname,
                    "user": host.user,
                    "port": host.port,
                    "container": host.container,
                    "identity_file": host.identity_file,
                    "known_hosts_file": host.known_hosts_file,
                    "connect_timeout": host.connect_timeout,
                }
                for host in self.all()
            ],
        }
        temporary = self._storage_path.with_suffix(self._storage_path.suffix + ".tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        os.chmod(temporary, 0o600)
        temporary.replace(self._storage_path)
