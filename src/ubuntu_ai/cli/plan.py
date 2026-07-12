import typer
from rich.console import Console
from rich.table import Table

from ubuntu_ai.planner.planner import Planner

console = Console()


def plan(request: str = typer.Argument(..., help="Solicitação a ser planejada.")) -> None:
    """Gera um plano sem executar comandos."""

    planner = Planner()

    try:
        generated_plan = planner.create_plan(request)
    except ValueError as error:
        console.print(f"[red]Erro:[/red] {error}")
        raise typer.Exit(code=1) from error

    table = Table(title=generated_plan.goal)

    table.add_column("#", justify="right")
    table.add_column("Etapa")
    table.add_column("Descrição")
    table.add_column("Comando")

    for index, step in enumerate(generated_plan.steps, start=1):
        table.add_row(
            str(index),
            step.title,
            step.description,
            " ".join(step.command),
        )

    console.print(f"[bold]Risco:[/bold] {generated_plan.risk.value.upper()}")
    console.print(f"[bold]Tempo estimado:[/bold] {generated_plan.estimated_seconds} segundos")
    console.print(table)
    console.print("[yellow]Nenhum comando foi executado.[/yellow]")
