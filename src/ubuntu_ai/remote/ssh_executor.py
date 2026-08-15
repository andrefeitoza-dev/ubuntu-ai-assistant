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

        result = self._runner.run(
            (
                "ssh",
                "-p",
                str(host.port),
                "--",
                target,
                remote_command,
            ),
            timeout=command.timeout,
        )

        return RemoteExecutionResult(
            host=host.name,
            command=command.argv,
            return_code=result.return_code,
            stdout=result.stdout,
            stderr=result.stderr,
        )
