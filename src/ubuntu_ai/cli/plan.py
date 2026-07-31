import typer
from rich.console import Console

from ubuntu_ai.cli.context import CLIContext
from ubuntu_ai.cli.errors import render_cli_error
from ubuntu_ai.container.bootstrap import container

console = Console()


def plan(
    ctx: typer.Context,
    request: str = typer.Argument(..., help="Solicitação a ser planejada."),
) -> None:
    """Gera e exibe uma prévia segura, sem executar comandos."""

    pipeline = container.execution_pipeline()
    cli_context = ctx.ensure_object(CLIContext)

    try:
        with console.status(
            "[bold cyan]Gerando plano com o modelo local...[/bold cyan]"
        ):
            result = pipeline.run(request)
    except (RuntimeError, ValueError) as error:
        if cli_context.debug:
            raise
        render_cli_error(console, error, title="Erro ao gerar o plano.")
        raise typer.Exit(code=1) from error

    console.print(result.rendered_preview)
