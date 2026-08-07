from __future__ import annotations

from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteExecutionResult,
    RemoteHost,
    RemoteHostKind,
)
from ubuntu_ai.remote.runner import ProcessRunner


class LocalExecutor:
    """Executa comandos no host local pela mesma interface remota."""

    def __init__(self, runner: ProcessRunner | None = None) -> None:
        self._runner = runner or ProcessRunner()

    def execute(
        self,
        host: RemoteHost,
        command: RemoteCommand,
    ) -> RemoteExecutionResult:
        if host.kind is not RemoteHostKind.LOCAL:
            raise ValueError("LocalExecutor exige host local.")

        result = self._runner.run(
            command.argv,
            timeout=command.timeout,
        )

        return RemoteExecutionResult(
            host=host.name,
            command=command.argv,
            return_code=result.return_code,
            stdout=result.stdout,
            stderr=result.stderr,
        )
