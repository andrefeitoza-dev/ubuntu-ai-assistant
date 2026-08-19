from __future__ import annotations

from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteExecutionResult,
    RemoteHost,
    RemoteHostKind,
)
from ubuntu_ai.remote.runner import ProcessRunner


class DockerExecutor:
    """Executa comandos em containers já existentes."""

    def __init__(self, runner: ProcessRunner | None = None) -> None:
        self._runner = runner or ProcessRunner()

    def execute(
        self,
        host: RemoteHost,
        command: RemoteCommand,
    ) -> RemoteExecutionResult:
        if host.kind is not RemoteHostKind.DOCKER:
            raise ValueError("DockerExecutor exige host Docker.")

        result = self._runner.run(
            (
                "docker",
                "exec",
                str(host.container),
                *command.argv,
            ),
            timeout=command.timeout,
            cancellation=command.cancellation,
        )

        return RemoteExecutionResult(
            host=host.name,
            command=command.argv,
            return_code=result.return_code,
            stdout=result.stdout,
            stderr=result.stderr,
        )
