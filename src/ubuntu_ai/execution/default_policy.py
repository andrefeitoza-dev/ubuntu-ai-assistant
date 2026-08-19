from __future__ import annotations

import os
import shlex
from pathlib import Path
from urllib.parse import urlparse

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
    _TRUSTED_DESKTOP_APPS = frozenset(
        {
            "code",
            "firefox",
            "org.gnome.Calculator",
            "org.gnome.Nautilus",
            "org.gnome.Settings",
            "org.gnome.Terminal",
        }
    )

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

        try:
            arguments = shlex.split(command)
        except ValueError:
            return PolicyDecision(False, "Comando com argumentos inválidos.")

        executable = arguments[0]

        if executable in self._BLOCKED_COMMANDS:
            return PolicyDecision(
                allowed=False,
                reason=f"Comando '{executable}' bloqueado pela política.",
            )

        if executable == "xdg-open" and not self._valid_open_target(arguments):
            return PolicyDecision(
                allowed=False,
                reason="Destino bloqueado pela política de ações desktop.",
            )

        if executable == "gtk-launch" and (
            len(arguments) != 2 or arguments[1] not in self._TRUSTED_DESKTOP_APPS
        ):
            return PolicyDecision(
                allowed=False,
                reason="Aplicativo bloqueado pela política de ações desktop.",
            )

        return PolicyDecision(
            allowed=True,
            reason="Comando autorizado.",
        )

    @staticmethod
    def _valid_open_target(arguments: list[str]) -> bool:
        if len(arguments) != 2:
            return False
        target = arguments[1]
        parsed = urlparse(target)
        if parsed.scheme:
            return (
                parsed.scheme in {"http", "https"}
                and bool(parsed.hostname)
                and not parsed.username
                and not parsed.password
            )

        try:
            home = Path.home().resolve()
            path = Path(target).resolve(strict=True)
            path.relative_to(home)
        except (OSError, RuntimeError, ValueError):
            return False
        return os.access(path, os.R_OK)
