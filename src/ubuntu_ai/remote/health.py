from __future__ import annotations

from dataclasses import dataclass

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
        except (OSError, TimeoutError, ValueError) as exc:
            return RemoteHealth(
                healthy=False,
                message=str(exc),
            )

        return RemoteHealth(
            healthy=result.success,
            message=(
                "Host disponível."
                if result.success
                else result.stderr or "Falha de conectividade."
            ),
        )
