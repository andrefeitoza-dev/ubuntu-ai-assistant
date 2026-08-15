from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.remote.models import RemoteCommand, RemoteHost


@dataclass(frozen=True, slots=True)
class RemotePolicyDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str


class RemoteExecutionPolicy:
    """Aplica guardrails mínimos antes de execução remota."""

    _DESTRUCTIVE = {
        "rm",
        "shutdown",
        "reboot",
        "mkfs",
        "fdisk",
        "parted",
    }

    def evaluate(
        self,
        host: RemoteHost,
        command: RemoteCommand,
    ) -> RemotePolicyDecision:
        executable = command.argv[0].lower()

        if executable in self._DESTRUCTIVE:
            return RemotePolicyDecision(
                allowed=True,
                requires_confirmation=True,
                reason=(f"Comando potencialmente destrutivo em {host.name}."),
            )

        return RemotePolicyDecision(
            allowed=True,
            requires_confirmation=False,
            reason="Execução remota permitida.",
        )
