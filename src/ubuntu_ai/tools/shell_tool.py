from typing import Any

from ubuntu_ai.services.shell import CommandResult, ShellService
from ubuntu_ai.tools.base import Tool


class ShellTool(Tool):
    """Executa comandos por meio do ShellService."""

    name = "shell"
    description = "Executa comandos seguros no sistema operacional."

    def __init__(self, shell_service: ShellService | None = None) -> None:
        self._shell_service = shell_service or ShellService()

    def execute(self, **kwargs: Any) -> CommandResult:
        command = kwargs.get("command")
        timeout = kwargs.get("timeout", 30)

        if not isinstance(command, list) or not all(isinstance(item, str) for item in command):
            raise ValueError("O parâmetro 'command' deve ser uma lista de strings.")

        if not isinstance(timeout, int) or timeout <= 0:
            raise ValueError("O parâmetro 'timeout' deve ser um inteiro positivo.")

        return self._shell_service.run(
            command=command,
            timeout=timeout,
        )
