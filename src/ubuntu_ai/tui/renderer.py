from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ubuntu_ai.agent_loop.models import LoopSnapshot, LoopState
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.memory.models import ExecutionRecord
from ubuntu_ai.plugins.registry import LoadedPlugin


_STATE_LABELS = {
    LoopState.IDLE: "ocioso",
    LoopState.PLANNING: "planejando",
    LoopState.WAITING_CONFIRMATION: "aguardando confirmação",
    LoopState.EXECUTING: "executando",
    LoopState.REPLANNING: "replanejando",
    LoopState.COMPLETED: "concluído",
    LoopState.BLOCKED: "bloqueado",
    LoopState.FAILED: "falhou",
    LoopState.CANCELLED: "cancelado",
}

_STATUS_STYLES = {
    ExecutionStatus.APPROVED: "cyan",
    ExecutionStatus.BLOCKED: "yellow",
    ExecutionStatus.EXECUTED: "green",
    ExecutionStatus.FAILED: "red",
}


class TerminalRenderer:
    """Renderiza o Agent Loop em uma interface baseada em Rich."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def banner(self) -> None:
        self.console.print(
            Panel.fit(
                "[bold]Ubuntu AI Assistant[/bold]\n"
                "Agente local com planejamento e confirmação segura",
                border_style="blue",
            )
        )
        self.help(compact=True)

    def help(self, *, compact: bool = False) -> None:
        commands = (
            "[cyan]:help[/cyan] ajuda  "
            "[cyan]:status[/cyan] estado  "
            "[cyan]:history[/cyan] histórico  "
            "[cyan]:plugins[/cyan] plugins  "
            "[cyan]:quit[/cyan] sair"
        )
        if compact:
            self.console.print(commands)
            return
        self.console.print(Panel(commands, title="Comandos", border_style="cyan"))

    def plan(self, snapshot: LoopSnapshot) -> None:
        pending = snapshot.pending_plan
        if pending is None:
            self.console.print("[yellow]Nenhum plano pendente.[/yellow]")
            return
        self.console.print(
            Panel(
                pending.message,
                title=f"Plano — iteração {snapshot.iteration}",
                border_style="magenta",
            )
        )

    def status(self, snapshot: LoopSnapshot) -> None:
        table = Table(title="Estado do Agent Loop", show_header=False)
        table.add_column("Campo", style="bold")
        table.add_column("Valor")
        table.add_row("Objetivo", snapshot.goal or "—")
        table.add_row("Estado", _STATE_LABELS[snapshot.state])
        table.add_row("Iteração", str(snapshot.iteration))
        table.add_row("Execuções", str(len(snapshot.records)))
        table.add_row(
            "Motivo de parada",
            snapshot.stop_reason.value if snapshot.stop_reason else "—",
        )
        self.console.print(table)

    def results(self, results: tuple[ExecutionResult, ...]) -> None:
        if not results:
            self.console.print("[yellow]A execução não retornou resultados.[/yellow]")
            return
        table = Table(title="Resultados da execução")
        table.add_column("Status")
        table.add_column("Comando")
        table.add_column("Mensagem")
        table.add_column("Tempo", justify="right")
        for result in results:
            style = _STATUS_STYLES[result.status]
            duration = (
                f"{result.duration:.2f}s" if result.duration is not None else "—"
            )
            table.add_row(
                Text(result.status.value, style=style),
                result.command or "—",
                result.message,
                duration,
            )
        self.console.print(table)

    def history(self, records: tuple[ExecutionRecord, ...]) -> None:
        if not records:
            self.console.print("[yellow]Nenhuma execução persistida.[/yellow]")
            return
        table = Table(title="Histórico recente")
        table.add_column("Data")
        table.add_column("Status")
        table.add_column("Projeto")
        table.add_column("Comando")
        for record in records:
            table.add_row(
                record.created_at.astimezone().strftime("%Y-%m-%d %H:%M:%S"),
                record.status,
                record.project_name or "—",
                record.command,
            )
        self.console.print(table)

    def plugins(self, plugins: tuple[LoadedPlugin, ...]) -> None:
        if not plugins:
            self.console.print("[yellow]Nenhum plugin carregado.[/yellow]")
            return
        table = Table(title="Plugins carregados")
        table.add_column("Nome")
        table.add_column("Versão")
        table.add_column("API")
        for plugin in plugins:
            table.add_row(
                plugin.manifest.name,
                plugin.manifest.version,
                str(plugin.manifest.api_version),
            )
        self.console.print(table)

    def completion(self, snapshot: LoopSnapshot) -> None:
        style = {
            LoopState.COMPLETED: "green",
            LoopState.BLOCKED: "yellow",
            LoopState.FAILED: "red",
            LoopState.CANCELLED: "dim",
        }.get(snapshot.state, "blue")
        message = snapshot.events[-1].message if snapshot.events else _STATE_LABELS[snapshot.state]
        self.console.print(
            Panel(
                message,
                title=f"Ciclo {_STATE_LABELS[snapshot.state]}",
                border_style=style,
            )
        )
