import typer
from rich.console import Console

from ubuntu_ai.cli.context import CLIContext
from ubuntu_ai.cli.errors import render_cli_error
from ubuntu_ai.container.bootstrap import container

console = Console()


def shell(ctx: typer.Context) -> None:
    """Alias do modo interativo."""

    cli_context = ctx.ensure_object(CLIContext)

    try:
        container.terminal_app().run()
    except (KeyboardInterrupt, EOFError):
        raise typer.Exit(code=0) from None
    except Exception as error:
        if cli_context.debug:
            raise
        render_cli_error(
            console,
            error,
            title="A interface foi encerrada por um erro.",
        )
        raise typer.Exit(code=1) from error
