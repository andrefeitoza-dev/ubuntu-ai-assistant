from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class CommandOutput:
    command: str
    stdout: str
    stderr: str = ""


class ResponseFormatter:
    """Formata a saída dos comandos para uma apresentação amigável."""

    def format(self, output: CommandOutput) -> str:
        command = output.command.strip()

        if command.startswith("pwd"):
            return self._pwd(output.stdout)

        if command.startswith("df"):
            return self._disk(output.stdout)

        if command.startswith("free"):
            return self._memory(output.stdout)

        if command.startswith("ls"):
            return self._ls(output.stdout)

        return output.stdout.strip()

    def _pwd(self, stdout: str) -> str:
        return (
            "📂 Diretório Atual\n\n"
            f"{stdout.strip()}"
        )

    def _disk(self, stdout: str) -> str:
        return (
            "💾 Uso de Disco\n\n"
            f"{stdout.strip()}"
        )

    def _memory(self, stdout: str) -> str:
        return (
            "🧠 Memória RAM\n\n"
            f"{stdout.strip()}"
        )

    def _ls(self, stdout: str) -> str:
        return (
            "📁 Arquivos\n\n"
            f"{stdout.strip()}"
        )