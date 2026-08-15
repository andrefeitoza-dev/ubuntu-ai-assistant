from __future__ import annotations

from collections.abc import Callable

from rich.console import Console

from ubuntu_ai.agent_loop.controller import AgentLoopController
from ubuntu_ai.agent_loop.models import LoopSnapshot, LoopState
from ubuntu_ai.memory.service import MemoryService
from ubuntu_ai.plugins.registry import PluginRegistry
from ubuntu_ai.tui.models import TerminalAppConfig, TerminalCommand
from ubuntu_ai.tui.renderer import TerminalRenderer

InputReader = Callable[[str], str]


class TerminalApp:
    """Interface interativa para operar o Agent Loop pelo terminal."""

    def __init__(
        self,
        controller: AgentLoopController,
        memory_service: MemoryService,
        plugin_registry: PluginRegistry,
        *,
        console: Console | None = None,
        input_reader: InputReader | None = None,
        config: TerminalAppConfig | None = None,
    ) -> None:
        self._controller = controller
        self._memory_service = memory_service
        self._plugin_registry = plugin_registry
        self._console = console or Console()
        self._renderer = TerminalRenderer(self._console)
        self._input = input_reader or self._console.input
        self._config = config or TerminalAppConfig()

    def run(self) -> None:
        """Inicia o loop interativo até o usuário solicitar a saída."""

        self._renderer.banner()
        while True:
            raw_value = self._input("\n[bold cyan]ubuntu-ai >[/bold cyan] ").strip()
            if not raw_value:
                continue
            if self._handle_command(raw_value):
                if raw_value.lower() == TerminalCommand.QUIT:
                    return
                continue
            self._run_goal(raw_value)

    def _run_goal(self, goal: str) -> None:
        if self._config.clear_between_tasks:
            self._console.clear()
        try:
            with self._console.status("[bold cyan]Gerando plano com o modelo local...[/bold cyan]"):
                snapshot = self._controller.start(goal)
        except (RuntimeError, ValueError) as error:
            self._console.print(f"[red]Não foi possível gerar o plano:[/red] {error}")
            return

        pending = snapshot.pending_plan
        if (
            pending is not None
            and pending.pipeline_result is not None
            and pending.pipeline_result.intent is not None
        ):
            self._renderer.intent(pending.pipeline_result.intent)

        self._renderer.plan(snapshot)

        while snapshot.requires_confirmation:
            decision = self._input("[bold]Confirmar este plano?[/bold] [s/N/c] ").strip().lower()
            if decision in {"s", "sim", "y", "yes"}:
                snapshot = self._controller.confirm()
                self._render_latest_results(snapshot)
                if snapshot.requires_confirmation:
                    self._renderer.plan(snapshot)
                continue
            if decision in {"c", "cancelar", "cancel"}:
                snapshot = self._controller.cancel()
                break
            self._console.print("[yellow]Plano não executado.[/yellow]")
            snapshot = self._controller.cancel()
            break

        self._renderer.completion(snapshot)

    def _render_latest_results(self, snapshot: LoopSnapshot) -> None:
        if not snapshot.records:
            return
        self._renderer.results(snapshot.records[-1].execution_results)

    def _handle_command(self, raw_value: str) -> bool:
        command = raw_value.lower()
        if command == TerminalCommand.HELP:
            self._renderer.help()
            return True
        if command == TerminalCommand.STATUS:
            self._renderer.status(self._controller.snapshot())
            return True
        if command == TerminalCommand.HISTORY:
            records = self._memory_service.recent_executions(limit=self._config.history_limit)
            self._renderer.history(records)
            return True
        if command == TerminalCommand.PLUGINS:
            self._renderer.plugins(self._plugin_registry.all())
            return True
        if command == TerminalCommand.QUIT:
            snapshot = self._controller.snapshot()
            if snapshot.state in {
                LoopState.WAITING_CONFIRMATION,
                LoopState.PLANNING,
                LoopState.REPLANNING,
            }:
                self._controller.cancel()
            self._console.print("[dim]Ubuntu AI encerrado.[/dim]")
            return True
        if command.startswith(":"):
            self._console.print(f"[red]Comando desconhecido:[/red] {raw_value}. Use :help.")
            return True
        return False
