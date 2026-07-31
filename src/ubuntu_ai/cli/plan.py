import typer
from rich.console import Console

from ubuntu_ai.container.bootstrap import container

console = Console()


def plan(request: str = typer.Argument(..., help="Solicitação a ser planejada.")) -> None:
    """Gera e exibe uma prévia segura, sem executar comandos."""

    pipeline = container.execution_pipeline()

    try:
        with console.status(
            "[bold cyan]Gerando plano com o modelo local...[/bold cyan]"
        ):
            result = pipeline.run(request)
    except (RuntimeError, ValueError) as error:
        console.print(f"[red]Erro:[/red] {error}")
        raise typer.Exit(code=1) from error

    console.print(result.rendered_preview)
