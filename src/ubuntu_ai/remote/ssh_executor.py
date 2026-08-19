from __future__ import annotations

import shlex

from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteExecutionResult,
    RemoteHost,
    RemoteHostKind,
)
from ubuntu_ai.remote.runner import ProcessRunner


class SSHExecutor:
    """Executa comandos em hosts SSH usando o cliente OpenSSH do sistema."""

    def __init__(self, runner: ProcessRunner | None = None) -> None:
        self._runner = runner or ProcessRunner()

    def execute(
        self,
        host: RemoteHost,
        command: RemoteCommand,
    ) -> RemoteExecutionResult:
        if host.kind is not RemoteHostKind.SSH:
            raise ValueError("SSHExecutor exige um host SSH.")

        target = f"{host.user}@{host.hostname}" if host.user else str(host.hostname)

        remote_command = shlex.join(command.argv)

        ssh_argv = [
            "ssh",
            "-o",
            "BatchMode=yes",
            "-o",
            "PasswordAuthentication=no",
            "-o",
            "KbdInteractiveAuthentication=no",
            "-o",
            "StrictHostKeyChecking=yes",
            "-o",
            f"ConnectTimeout={int(host.connect_timeout)}",
            "-p",
            str(host.port),
        ]
        if host.identity_file:
            ssh_argv.extend(("-i", host.identity_file, "-o", "IdentitiesOnly=yes"))
        if host.known_hosts_file:
            ssh_argv.extend(("-o", f"UserKnownHostsFile={host.known_hosts_file}"))
        ssh_argv.extend(("--", target, remote_command))

        result = self._runner.run(
            ssh_argv,
            timeout=command.timeout,
        )

        return RemoteExecutionResult(
            host=host.name,
            command=command.argv,
            return_code=result.return_code,
            stdout=result.stdout,
            stderr=result.stderr,
        )
