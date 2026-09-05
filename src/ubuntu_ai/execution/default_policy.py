from __future__ import annotations

import os
import shlex
from pathlib import Path
from urllib.parse import urlparse

from ubuntu_ai.desktop import DesktopApplicationCatalog
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
    _BLOCKED_DIRECT_DESKTOP_EXECUTABLES = frozenset(
        {
            "gnome-calculator",
            "gnome-terminal",
            "libreoffice",
        }
    )
    _TRUSTED_DESKTOP_APPS = frozenset(
        {
            "code",
            "firefox",
            "libreoffice-startcenter",
            "org.gnome.Calculator",
            "org.gnome.Nautilus",
            "org.gnome.Settings",
            "org.gnome.Terminal",
        }
    )
    _PRIVILEGED_COMMANDS = frozenset(
        {
            ("apt-get", "update"),
            ("apt-get", "upgrade", "-y"),
            ("apt-get", "autoremove", "-y"),
            ("apt-get", "clean"),
            ("ufw", "enable"),
        }
    )

    def __init__(self, applications: DesktopApplicationCatalog | None = None) -> None:
        self._applications = applications or DesktopApplicationCatalog()

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

        if executable == "pkexec" and tuple(arguments[1:]) not in self._PRIVILEGED_COMMANDS:
            return PolicyDecision(
                allowed=False,
                reason="Comando privilegiado fora da lista segura.",
            )

        if executable in self._BLOCKED_COMMANDS:
            return PolicyDecision(
                allowed=False,
                reason=f"Comando '{executable}' bloqueado pela política.",
            )

        if executable in self._BLOCKED_DIRECT_DESKTOP_EXECUTABLES:
            return PolicyDecision(
                allowed=False,
                reason="Aplicativo desktop deve usar uma entrada confiável.",
            )

        if executable == "firefox" and not self._valid_firefox(arguments):
            return PolicyDecision(
                allowed=False,
                reason="Destino bloqueado para abertura no Firefox.",
            )

        if executable == "xdg-open" and not self._valid_open_target(arguments):
            return PolicyDecision(
                allowed=False,
                reason="Destino bloqueado pela política de ações desktop.",
            )

        if executable == "gtk-launch" and not self._valid_desktop_launch(arguments):
            return PolicyDecision(
                allowed=False,
                reason="Aplicativo bloqueado pela política de ações desktop.",
            )

        if executable in {"mkdir", "cp", "mv"} and not self._valid_file_change(arguments):
            return PolicyDecision(
                allowed=False,
                reason="Alteração de arquivo bloqueada pela política de caminhos seguros.",
            )

        if executable == "gio" and not self._valid_trash(arguments):
            return PolicyDecision(
                allowed=False,
                reason="Operação de Lixeira bloqueada pela política de caminhos seguros.",
            )

        return PolicyDecision(
            allowed=True,
            reason="Comando autorizado.",
        )

    def _valid_desktop_launch(self, arguments: list[str]) -> bool:
        if len(arguments) != 2:
            return False
        desktop_id = arguments[1]
        return desktop_id in self._TRUSTED_DESKTOP_APPS or self._applications.contains_id(
            desktop_id
        )

    @staticmethod
    def _valid_file_change(arguments: list[str]) -> bool:
        executable = arguments[0]
        expected = 2 if executable == "mkdir" else 3
        if len(arguments) != expected:
            return False
        try:
            home = Path.home().resolve()
            paths = [Path(value) for value in arguments[1:]]
            for path in paths:
                if not path.is_absolute() or path.is_symlink():
                    return False
                path.resolve(strict=False).relative_to(home)
            destination = paths[-1]
            if destination.exists():
                return False
            if executable == "mkdir":
                return destination.parent.is_dir() and not destination.parent.is_symlink()
            source = paths[0]
            return source.exists() and not source.is_symlink() and destination.parent.is_dir()
        except (OSError, RuntimeError, ValueError):
            return False

    @staticmethod
    def _valid_trash(arguments: list[str]) -> bool:
        if len(arguments) != 3 or arguments[1] != "trash":
            return False
        try:
            home = Path.home().resolve()
            source = Path(arguments[2])
            return (
                source.is_absolute()
                and source.exists()
                and not source.is_symlink()
                and source.resolve(strict=True).is_relative_to(home)
            )
        except (OSError, RuntimeError, ValueError):
            return False

    @staticmethod
    def _valid_firefox(arguments: list[str]) -> bool:
        if len(arguments) == 1:
            return True
        if len(arguments) != 2:
            return False
        return DefaultExecutionPolicy._valid_http_url(arguments[1])

    @staticmethod
    def _valid_open_target(arguments: list[str]) -> bool:
        if len(arguments) != 2:
            return False
        target = arguments[1]
        parsed = urlparse(target)
        if parsed.scheme:
            return DefaultExecutionPolicy._valid_http_url(target)

        try:
            home = Path.home().resolve()
            path = Path(target).resolve(strict=True)
            path.relative_to(home)
        except (OSError, RuntimeError, ValueError):
            return False
        return os.access(path, os.R_OK)

    @staticmethod
    def _valid_http_url(target: str) -> bool:
        if not target or any(ord(character) < 32 or ord(character) == 127 for character in target):
            return False
        parsed = urlparse(target)
        try:
            parsed.port
        except ValueError:
            return False
        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.hostname)
            and not parsed.username
            and not parsed.password
        )
