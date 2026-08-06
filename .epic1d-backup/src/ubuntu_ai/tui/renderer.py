from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ubuntu_ai.agent_loop.models import LoopSnapshot, LoopState
from ubuntu_ai.benchmark import BenchmarkReport
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

_STATUS_SYMBOLS = {
    ExecutionStatus.APPROVED: "●",
    ExecutionStatus.BLOCKED: "■",
    ExecutionStatus.EXECUTED: "✓",
    ExecutionStatus.FAILED: "✗",
}


class TerminalRenderer:
    """Renderiza o Agent Loop em uma interface baseada em Rich."""

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()

    def banner(self) -> None:
        title = Text("Ubuntu AI Assistant", style="bold white")
        subtitle = Text(
            "Agente local para Linux com planejamento e execução segura",
            style="dim",
        )
        self.console.print(
            Panel.fit(
                Text.assemble(title, "\n", subtitle),
                border_style="bright_blue",
                padding=(1, 3),
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
                title=f"Plano · iteração {snapshot.iteration}",
                subtitle="Revise antes de confirmar",
                border_style="magenta",
                padding=(1, 2),
            )
        )

    def status(self, snapshot: LoopSnapshot) -> None:
        table = Table(title="Estado do Agent Loop", show_header=False, box=None)
        table.add_column("Campo", style="bold cyan")
        table.add_column("Valor")
        table.add_row("Objetivo", snapshot.goal or "—")
        table.add_row("Estado", _STATE_LABELS[snapshot.state])
        table.add_row("Iteração", str(snapshot.iteration))
        table.add_row("Execuções", str(len(snapshot.records)))
        table.add_row(
            "Motivo de parada",
            snapshot.stop_reason.value if snapshot.stop_reason else "—",
        )
        self.console.print(Panel(table, border_style="blue"))

    def results(self, results: tuple[ExecutionResult, ...]) -> None:
        if not results:
            self.console.print("[yellow]A execução não retornou resultados.[/yellow]")
            return
        table = Table(title="Resultados da execução", header_style="bold")
        table.add_column("", width=2)
        table.add_column("Status")
        table.add_column("Comando", overflow="fold")
        table.add_column("Mensagem", overflow="fold")
        table.add_column("Tempo", justify="right")
        for result in results:
            style = _STATUS_STYLES[result.status]
            duration = (
                f"{result.duration:.2f}s" if result.duration is not None else "—"
            )
            table.add_row(
                Text(_STATUS_SYMBOLS[result.status], style=style),
                Text(result.status.value, style=style),
                result.command or "—",
                result.message,
                duration,
            )
        self.console.print(table)

    def benchmark(self, report: BenchmarkReport) -> None:
        if not report.records:
            return
        table = Table(title="Desempenho", show_header=True, header_style="bold cyan")
        table.add_column("Operação")
        table.add_column("Tempo", justify="right")
        table.add_column("Estado", justify="center")
        for record in report.records:
            table.add_row(
                record.operation,
                f"{record.duration:.3f}s",
                "[green]OK[/green]" if record.success else "[red]FALHA[/red]",
            )
        table.add_section()
        table.add_row("Total", f"{report.total_duration:.3f}s", "")
        table.add_row("Média", f"{report.average_duration:.3f}s", "")
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
        symbol = {
            LoopState.COMPLETED: "✓",
            LoopState.BLOCKED: "■",
            LoopState.FAILED: "✗",
            LoopState.CANCELLED: "●",
        }.get(snapshot.state, "●")
        message = (
            snapshot.events[-1].message
            if snapshot.events
            else _STATE_LABELS[snapshot.state]
        )
        self.console.print(
            Panel(
                f"[bold]{symbol} {message}[/bold]",
                title=f"Ciclo {_STATE_LABELS[snapshot.state]}",
                border_style=style,
            )
        )
