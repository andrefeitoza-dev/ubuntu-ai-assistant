from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


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

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("O nome do host não pode estar vazio.")

        if self.kind is RemoteHostKind.SSH and not self.hostname:
            raise ValueError("Hosts SSH exigem hostname.")

        if self.kind is RemoteHostKind.DOCKER and not self.container:
            raise ValueError("Hosts Docker exigem container.")

        if not 1 <= self.port <= 65535:
            raise ValueError("Porta inválida.")


@dataclass(frozen=True, slots=True)
class RemoteCommand:
    """Comando solicitado para um destino."""

    argv: tuple[str, ...]
    timeout: float = 30.0

    def __post_init__(self) -> None:
        if not self.argv:
            raise ValueError("O comando não pode estar vazio.")
        if self.timeout <= 0:
            raise ValueError("timeout deve ser maior que zero.")


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
