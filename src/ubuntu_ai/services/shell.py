import os
import subprocess
import tempfile
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

    _LAUNCH_CHECK_SECONDS = 0.5
    _TRUSTED_EXECUTABLE_PATH = (
        "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"
    )
    _TRUSTED_XDG_DATA_DIRS = "/usr/local/share:/usr/share:/var/lib/snapd/desktop"
    _UNSAFE_INHERITED_ENVIRONMENT = frozenset(
        {
            "GIO_LAUNCHED_DESKTOP_FILE",
            "GIO_LAUNCHED_DESKTOP_FILE_PID",
            "GIO_EXTRA_MODULES",
            "GTK_DATA_PREFIX",
            "GTK_EXE_PREFIX",
            "GTK_PATH",
            "LD_LIBRARY_PATH",
            "LD_PRELOAD",
            "LOCPATH",
            "PYTHONHOME",
        }
    )

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

    def launch(self, command: list[str]) -> CommandResult:
        """Inicia um processo gráfico e detecta falhas de partida imediatas."""

        environment = os.environ.copy()
        for variable in self._UNSAFE_INHERITED_ENVIRONMENT:
            environment.pop(variable, None)
        environment["PATH"] = self._TRUSTED_EXECUTABLE_PATH
        environment["XDG_DATA_DIRS"] = self._TRUSTED_XDG_DATA_DIRS

        with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as stdout_file:
            with tempfile.TemporaryFile(mode="w+t", encoding="utf-8") as stderr_file:
                process = subprocess.Popen(
                    command,
                    stdin=subprocess.DEVNULL,
                    stdout=stdout_file,
                    stderr=stderr_file,
                    start_new_session=True,
                    env=environment,
                )
                try:
                    return_code = process.wait(timeout=self._LAUNCH_CHECK_SECONDS)
                except subprocess.TimeoutExpired:
                    return_code = 0

                stdout_file.seek(0)
                stderr_file.seek(0)
                stdout = stdout_file.read().strip()
                stderr = stderr_file.read().strip()

        return CommandResult(
            command=" ".join(command),
            return_code=return_code,
            stdout=stdout,
            stderr=stderr,
        )
