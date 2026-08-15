from __future__ import annotations

import typer
from rich.console import Console

from ubuntu_ai.cli.context import CLIContext
from ubuntu_ai.cli.errors import render_cli_error
from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.tui.renderer import TerminalRenderer

console = Console()


def run(
    ctx: typer.Context,
    request: str = typer.Argument(..., help="Objetivo a ser planejado e executado."),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Confirma automaticamente as iterações do plano.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Gera o plano sem executar comandos.",
    ),
) -> None:
    """Executa o fluxo consolidado do Ubuntu AI Assistant."""

    cli_context = ctx.ensure_object(CLIContext)
    renderer = TerminalRenderer(console)
    runtime = container.application_runtime()

    try:
        with console.status("[bold cyan]Analisando contexto e gerando plano...[/bold cyan]"):
            snapshot = runtime.start(request)

        pending = snapshot.pending_plan
        if (
            pending is not None
            and pending.pipeline_result is not None
            and pending.pipeline_result.intent is not None
        ):
            renderer.intent(pending.pipeline_result.intent)

        renderer.plan(snapshot)

        if dry_run:
            console.print("[yellow]Dry-run: nenhuma execução foi confirmada.[/yellow]")
            return

        while snapshot.requires_confirmation:
            confirmed = yes or typer.confirm(
                "Confirmar este plano?",
                default=False,
            )

            if not confirmed:
                snapshot = runtime.cancel()
                renderer.completion(snapshot)
                return

            snapshot = runtime.confirm()

            if snapshot.records:
                renderer.results(snapshot.records[-1].execution_results)

            if snapshot.requires_confirmation:
                renderer.plan(snapshot)

        renderer.completion(snapshot)

    except (RuntimeError, ValueError) as error:
        if cli_context.debug:
            raise
        render_cli_error(
            console,
            error,
            title="Erro durante a execução.",
        )
        raise typer.Exit(code=1) from error
