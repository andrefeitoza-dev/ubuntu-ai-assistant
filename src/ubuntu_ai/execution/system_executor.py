from __future__ import annotations

import shlex
from time import perf_counter

from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)
from ubuntu_ai.services.shell import ShellService


class SystemExecutor:
    """Executa comandos reais por meio do ShellService."""

    _DETACHED_EXECUTABLES = frozenset({"gtk-launch", "xdg-open"})

    def __init__(
        self,
        shell_service: ShellService | None = None,
        timeout: int = 30,
    ) -> None:
        if timeout <= 0:
            raise ValueError("O timeout deve ser maior que zero.")

        self._shell_service = shell_service or ShellService()
        self._timeout = timeout

    def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Executa uma solicitação e converte o resultado do shell."""

        command = request.command.strip()

        if not command:
            raise ValueError("O comando não pode estar vazio.")

        if request.dry_run:
            return ExecutionResult(
                status=ExecutionStatus.APPROVED,
                message="Comando aprovado em modo de simulação.",
                command=command,
            )

        arguments = shlex.split(command)
        started_at = perf_counter()

        try:
            if arguments[0] in self._DETACHED_EXECUTABLES:
                command_result = self._shell_service.launch(arguments)
            else:
                command_result = self._shell_service.run(
                    arguments,
                    timeout=self._timeout,
                )
        except Exception as error:
            duration = perf_counter() - started_at

            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Falha ao executar o comando: {error}",
                command=command,
                stderr=str(error),
                duration=duration,
            )

        duration = perf_counter() - started_at

        if command_result.success:
            return ExecutionResult(
                status=ExecutionStatus.EXECUTED,
                message="Comando executado com sucesso.",
                command=command_result.command,
                return_code=command_result.return_code,
                stdout=command_result.stdout,
                stderr=command_result.stderr,
                duration=duration,
            )

        return ExecutionResult(
            status=ExecutionStatus.FAILED,
            message="O comando terminou com erro.",
            command=command_result.command,
            return_code=command_result.return_code,
            stdout=command_result.stdout,
            stderr=command_result.stderr,
            duration=duration,
        )
