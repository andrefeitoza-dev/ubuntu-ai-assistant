import subprocess
from dataclasses import dataclass


@dataclass(slots=True)
class CommandResult:
    command: str
    return_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.return_code == 0


class ShellService:
    """Executa comandos do sistema operacional."""

    def run(
        self,
        command: list[str],
        timeout: int = 30,
    ) -> CommandResult:

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return CommandResult(
            command=" ".join(command),
            return_code=process.returncode,
            stdout=process.stdout.strip(),
            stderr=process.stderr.strip(),
        )
