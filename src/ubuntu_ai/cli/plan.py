import typer
from rich.console import Console

from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline

console = Console()


def plan(request: str = typer.Argument(..., help="Solicitação a ser planejada.")) -> None:
    """Gera e exibe uma prévia segura, sem executar comandos."""

    pipeline = ExecutionPipeline()

    try:
        result = pipeline.run(request)
    except ValueError as error:
        console.print(f"[red]Erro:[/red] {error}")
        raise typer.Exit(code=1) from error

    console.print(result.rendered_preview)