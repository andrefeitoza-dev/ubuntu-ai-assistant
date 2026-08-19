from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

_HOST_NAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")
_USER_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_.-]{0,31}$")
_INVENTORY_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$")


class RemoteHostKind(StrEnum):
    """Tipos de destino suportados pela camada remota."""

    LOCAL = "local"
    SSH = "ssh"
    DOCKER = "docker"


@dataclass(frozen=True, slots=True)
class RemoteHost:
    """Definição não secreta de um host remoto."""

    name: str
    kind: RemoteHostKind
    hostname: str | None = None
    user: str | None = None
    port: int = 22
    container: str | None = None
    identity_file: str | None = None
    known_hosts_file: str | None = None
    connect_timeout: float = 10.0

    def __post_init__(self) -> None:
        name = self.name.strip()
        if not _INVENTORY_NAME.fullmatch(name):
            raise ValueError("Nome de host inválido para o inventário.")
        object.__setattr__(self, "name", name)

        if self.kind is RemoteHostKind.SSH:
            hostname = (self.hostname or "").strip()
            if not _HOST_NAME.fullmatch(hostname) or ".." in hostname:
                raise ValueError("Hosts SSH exigem hostname ou endereço IP válido.")
            object.__setattr__(self, "hostname", hostname)

            if self.user is not None:
                user = self.user.strip()
                if not _USER_NAME.fullmatch(user):
                    raise ValueError("Usuário SSH inválido.")
                object.__setattr__(self, "user", user)

            for field_name in ("identity_file", "known_hosts_file"):
                value = getattr(self, field_name)
                if value is None:
                    continue
                path = Path(value).expanduser()
                if not path.is_absolute():
                    raise ValueError(f"{field_name} deve usar caminho absoluto.")
                object.__setattr__(self, field_name, str(path))

        if self.kind is RemoteHostKind.DOCKER and not self.container:
            raise ValueError("Hosts Docker exigem container.")

        if not 1 <= self.port <= 65535:
            raise ValueError("Porta inválida.")

        if not 1 <= self.connect_timeout <= 60:
            raise ValueError("Timeout de conexão deve estar entre 1 e 60 segundos.")


@dataclass(frozen=True, slots=True)
class RemoteCommand:
    """Comando solicitado para um destino."""

    argv: tuple[str, ...]
    timeout: float = 30.0

    def __post_init__(self) -> None:
        if not self.argv:
            raise ValueError("O comando não pode estar vazio.")
        if any(
            not isinstance(argument, str) or not argument or "\0" in argument
            for argument in self.argv
        ):
            raise ValueError("Argumentos do comando devem ser textos não vazios e sem NUL.")
        if not 0 < self.timeout <= 300:
            raise ValueError("Timeout deve estar entre 0 e 300 segundos.")


@dataclass(frozen=True, slots=True)
class RemoteExecutionResult:
    """Resultado normalizado de uma execução."""

    host: str
    command: tuple[str, ...]
    return_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.return_code == 0
