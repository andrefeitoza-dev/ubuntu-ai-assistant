from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.remote.cancellation import RemoteExecutionCancelled
from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteHost,
    RemoteHostKind,
)


@dataclass(frozen=True, slots=True)
class RemoteHealth:
    healthy: bool
    message: str


class RemoteHealthService:
    """Valida disponibilidade de um destino usando uma execução mínima."""

    def check(self, engine, host: RemoteHost) -> RemoteHealth:
        command = (
            RemoteCommand(("true",), timeout=5.0)
            if host.kind is not RemoteHostKind.DOCKER
            else RemoteCommand(("sh", "-lc", "true"), timeout=5.0)
        )

        try:
            result = engine.execute(host.name, command)
        except (OSError, TimeoutError, ValueError, RemoteExecutionCancelled) as exc:
            return RemoteHealth(
                healthy=False,
                message=self._friendly_error(exc),
            )

        return RemoteHealth(
            healthy=result.success,
            message=(
                "Host disponível." if result.success else result.stderr or "Falha de conectividade."
            ),
        )

    @staticmethod
    def _friendly_error(error: Exception) -> str:
        message = str(error)
        lowered = message.lower()
        if isinstance(error, TimeoutError):
            return "O servidor não respondeu dentro do tempo configurado."
        if "host key verification failed" in lowered:
            return "A identidade SSH do servidor não pôde ser confirmada."
        if "permission denied" in lowered:
            return "A autenticação por chave SSH foi recusada pelo servidor."
        if "could not resolve hostname" in lowered:
            return "O endereço do servidor não pôde ser localizado."
        if isinstance(error, RemoteExecutionCancelled):
            return "Teste de conexão cancelado pelo usuário."
        return message or "Falha ao conectar ao servidor remoto."
