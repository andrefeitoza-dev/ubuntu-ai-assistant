from __future__ import annotations

from ubuntu_ai.execution.models import ExecutionRequest
from ubuntu_ai.execution.policy import (
    ExecutionPolicy,
    PolicyDecision,
)


class DefaultExecutionPolicy(ExecutionPolicy):
    """Política padrão de autorização de execução."""

    _BLOCKED_COMMANDS = {
        "rm",
        "mkfs",
        "dd",
        "shutdown",
        "reboot",
        "poweroff",
    }

    def evaluate(
        self,
        request: ExecutionRequest,
    ) -> PolicyDecision:
        command = request.command.strip()

        if not command:
            return PolicyDecision(
                allowed=False,
                reason="Comando vazio.",
            )

        executable = command.split()[0]

        if executable in self._BLOCKED_COMMANDS:
            return PolicyDecision(
                allowed=False,
                reason=f"Comando '{executable}' bloqueado pela política.",
            )

        return PolicyDecision(
            allowed=True,
            reason="Comando autorizado.",
        )