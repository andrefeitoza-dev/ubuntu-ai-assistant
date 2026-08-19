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
            detail = str(error)

            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=self._failure_message(detail),
                command=command,
                stderr=detail,
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
            message=self._failure_message(command_result.stderr),
            command=command_result.command,
            return_code=command_result.return_code,
            stdout=command_result.stdout,
            stderr=command_result.stderr,
            duration=duration,
        )

    @staticmethod
    def _failure_message(detail: str) -> str:
        normalized = detail.casefold()
        permission_markers = (
            "permission denied",
            "permissão negada",
            "operation not permitted",
            "operação não permitida",
            "errno 13",
        )
        if any(marker in normalized for marker in permission_markers):
            return (
                "A operação não foi executada porque o usuário atual não possui "
                "permissão. Nenhuma elevação automática foi tentada."
            )

        missing_markers = (
            "no such file or directory",
            "arquivo ou diretório inexistente",
            "errno 2",
        )
        if any(marker in normalized for marker in missing_markers):
            return "O recurso solicitado não foi encontrado."

        return "O comando terminou com erro."
