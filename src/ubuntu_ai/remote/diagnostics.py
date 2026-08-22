from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.remote.engine import RemoteExecutionEngine
from ubuntu_ai.remote.models import RemoteCommand, RemoteExecutionResult


@dataclass(frozen=True, slots=True)
class RemoteDiagnosticItem:
    name: str
    command: tuple[str, ...]
    output: str
    success: bool


@dataclass(frozen=True, slots=True)
class RemoteSystemContext:
    host_name: str
    items: tuple[RemoteDiagnosticItem, ...]

    def get(self, name: str) -> RemoteDiagnosticItem:
        for item in self.items:
            if item.name == name:
                return item
        raise KeyError(name)


class RemoteDiagnosticService:
    """Coleta contexto Ubuntu somente com consultas de leitura."""

    _COMMANDS = (
        ("system", ("uname", "-srmo")),
        ("cpu", ("nproc",)),
        ("memory", ("free", "-m")),
        ("disk", ("df", "-h", "/")),
        ("network", ("ip", "-brief", "address")),
        ("services", ("systemctl", "--failed", "--no-legend")),
    )
    _FACT_COMMANDS = {
        "operating_system": ("cat", "/etc/os-release"),
        "kernel": ("uname", "-srmo"),
        "hostname": ("hostname",),
        "cpu": ("nproc",),
        "memory": ("free", "-m"),
        "disk": ("df", "-h", "/"),
        "network": ("ip", "-brief", "address"),
        "battery": ("cat", "/sys/class/power_supply/BAT0/capacity"),
        "processes": ("ps", "-e", "-o", "pid="),
        "services": ("systemctl", "--failed", "--no-legend"),
    }
    _SUMMARY_TOPICS = (
        "operating_system",
        "kernel",
        "hostname",
        "cpu",
        "memory",
        "disk",
        "network",
        "battery",
        "processes",
        "services",
    )

    def __init__(self, engine: RemoteExecutionEngine) -> None:
        self._engine = engine

    def collect(self, host_name: str, *, timeout: float = 15.0) -> RemoteSystemContext:
        items = tuple(
            self._item(
                name, command, self._engine.execute(host_name, RemoteCommand(command, timeout))
            )
            for name, command in self._COMMANDS
        )
        return RemoteSystemContext(host_name=host_name, items=items)

    def answer_fact(
        self,
        host_name: str,
        topic: str,
        *,
        timeout: float = 15.0,
    ) -> str:
        """Responde uma consulta factual somente com comandos de leitura."""

        topics = self._SUMMARY_TOPICS if topic == "summary" else (topic,)
        unknown = [name for name in topics if name not in self._FACT_COMMANDS]
        if unknown:
            raise ValueError(f"Consulta remota não suportada: {unknown[0]}")

        items = tuple(
            self._item(
                name,
                self._FACT_COMMANDS[name],
                self._engine.execute(
                    host_name,
                    RemoteCommand(self._FACT_COMMANDS[name], timeout),
                ),
            )
            for name in topics
        )
        lines = [f"Computador remoto: {host_name}"]
        lines.extend(self._format_fact(item) for item in items)
        return "\n".join(lines)

    @classmethod
    def _format_fact(cls, item: RemoteDiagnosticItem) -> str:
        labels = {
            "operating_system": "Sistema",
            "kernel": "Kernel",
            "hostname": "Hostname",
            "cpu": "CPU",
            "memory": "Memória",
            "disk": "Disco",
            "network": "Rede",
            "battery": "Bateria",
            "processes": "Processos",
            "services": "Serviços",
        }
        label = labels[item.name]
        if not item.success:
            return f"{label}: indisponível ({item.output or 'sem detalhes'})"

        output = item.output.strip()
        if item.name == "operating_system":
            value = cls._os_name(output)
        elif item.name == "cpu":
            value = f"{output} CPU(s) lógica(s)"
        elif item.name == "memory":
            value = cls._memory_summary(output)
        elif item.name == "disk":
            value = cls._disk_summary(output)
        elif item.name == "network":
            value = output or "nenhuma interface ativa"
        elif item.name == "battery":
            value = f"{output}%" if output.isdigit() else (output or "indisponível")
        elif item.name == "processes":
            value = f"{sum(bool(line.strip()) for line in output.splitlines())} em execução"
        elif item.name == "services":
            failures = sum(bool(line.strip()) for line in output.splitlines())
            value = "nenhum em falha" if failures == 0 else f"{failures} em falha"
        else:
            value = output or "sem informação"
        return f"{label}: {value}"

    @staticmethod
    def _os_name(output: str) -> str:
        for line in output.splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.partition("=")[2].strip().strip('"')
        return output.splitlines()[0] if output else "indisponível"

    @staticmethod
    def _memory_summary(output: str) -> str:
        for line in output.splitlines():
            fields = line.split()
            if fields and fields[0].rstrip(":") == "Mem" and len(fields) >= 3:
                available = fields[-1]
                return f"{fields[1]} MiB no total · {available} MiB disponíveis"
        return output or "indisponível"

    @staticmethod
    def _disk_summary(output: str) -> str:
        lines = [line for line in output.splitlines() if line.strip()]
        if len(lines) < 2:
            return output or "indisponível"
        fields = lines[-1].split()
        if len(fields) < 5:
            return lines[-1]
        return f"{fields[4]} usado · {fields[3]} disponíveis"

    @staticmethod
    def _item(
        name: str,
        command: tuple[str, ...],
        result: RemoteExecutionResult,
    ) -> RemoteDiagnosticItem:
        output = result.stdout.strip() if result.success else result.stderr.strip()
        return RemoteDiagnosticItem(name, command, output, result.success)
