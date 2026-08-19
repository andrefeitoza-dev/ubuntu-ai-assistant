from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.remote.models import RemoteCommand, RemoteHost, RemoteHostKind


@dataclass(frozen=True, slots=True)
class RemotePolicyDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str
    risk: RiskLevel


class RemoteExecutionPolicy:
    """Aplica guardrails mínimos antes de execução remota."""

    _DESTRUCTIVE = {
        "rm",
        "shutdown",
        "reboot",
        "mkfs",
        "fdisk",
        "parted",
        "dd",
        "poweroff",
        "halt",
    }
    _SHELLS = {"bash", "dash", "sh", "zsh", "fish"}
    _ELEVATION = {"sudo", "su", "doas", "pkexec"}
    _READ_ONLY = {
        "cat",
        "df",
        "du",
        "free",
        "hostname",
        "hostnamectl",
        "ip",
        "journalctl",
        "ls",
        "lsblk",
        "lscpu",
        "nproc",
        "ps",
        "true",
        "uname",
        "uptime",
        "whoami",
    }
    _MODERATE = {"mkdir", "touch"}
    _SYSTEMCTL_READ_ONLY = {
        "--failed",
        "is-active",
        "is-enabled",
        "list-unit-files",
        "list-units",
        "show",
        "status",
    }

    def evaluate(
        self,
        host: RemoteHost,
        command: RemoteCommand,
    ) -> RemotePolicyDecision:
        executable = command.argv[0].lower()

        if executable in self._ELEVATION:
            return RemotePolicyDecision(
                allowed=False,
                requires_confirmation=False,
                reason="Elevação automática de privilégios não é permitida remotamente.",
                risk=RiskLevel.CRITICAL,
            )

        if executable in self._SHELLS and any(
            argument in {"-c", "-lc"} for argument in command.argv[1:]
        ):
            return RemotePolicyDecision(
                allowed=False,
                requires_confirmation=False,
                reason="Comandos remotos por interpretador de shell não são permitidos.",
                risk=RiskLevel.CRITICAL,
            )

        if executable in self._DESTRUCTIVE:
            return RemotePolicyDecision(
                allowed=True,
                requires_confirmation=True,
                reason=(f"Comando potencialmente destrutivo em {host.name}."),
                risk=RiskLevel.CRITICAL,
            )

        if host.kind is RemoteHostKind.SSH and executable == "systemctl":
            arguments = tuple(argument.lower() for argument in command.argv[1:])
            operation = (
                "--failed"
                if "--failed" in arguments
                else next((argument for argument in arguments if not argument.startswith("-")), "")
            )
            if operation not in self._SYSTEMCTL_READ_ONLY:
                return RemotePolicyDecision(
                    allowed=True,
                    requires_confirmation=True,
                    reason=f"Alteração de serviço exige confirmação para {host.name}.",
                    risk=RiskLevel.HIGH,
                )
            return RemotePolicyDecision(
                allowed=True,
                requires_confirmation=False,
                reason="Consulta remota de serviço permitida.",
                risk=RiskLevel.LOW,
            )

        if host.kind is RemoteHostKind.SSH and executable in self._MODERATE:
            return RemotePolicyDecision(
                allowed=True,
                requires_confirmation=True,
                reason=f"Alteração remota reversível exige confirmação para {host.name}.",
                risk=RiskLevel.MEDIUM,
            )

        if host.kind is RemoteHostKind.SSH and executable not in self._READ_ONLY:
            return RemotePolicyDecision(
                allowed=True,
                requires_confirmation=True,
                reason=f"Ação remota de alteração exige confirmação para {host.name}.",
                risk=RiskLevel.HIGH,
            )

        return RemotePolicyDecision(
            allowed=True,
            requires_confirmation=False,
            reason="Execução remota permitida.",
            risk=RiskLevel.LOW,
        )
