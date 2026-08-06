import typer
from rich.console import Console
from rich.table import Table

from ubuntu_ai.cli.context import CLIContext
from ubuntu_ai.cli.errors import render_cli_error
from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.intent.presenter import IntentPresenter

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

    detected_intent = getattr(result, "intent", None)
    if detected_intent is not None:
        view = IntentPresenter().present(detected_intent)
        table = Table(title="Intenção detectada", show_header=False)
        table.add_column("Campo", style="bold cyan")
        table.add_column("Valor")
        table.add_row("Categoria", view.category)
        table.add_row("Objetivo", view.goal)
        table.add_row("Confiança", view.confidence_percent)
        table.add_row("Entidades", view.entities)
        console.print(table)

    console.print(result.rendered_preview)
