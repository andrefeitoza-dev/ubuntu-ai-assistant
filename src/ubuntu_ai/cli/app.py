import typer

from ubuntu_ai.cli.benchmark import benchmark
from ubuntu_ai.cli.context import CLIContext
from ubuntu_ai.cli.diagnose_ai import diagnose_ai
from ubuntu_ai.cli.doctor import doctor
from ubuntu_ai.cli.knowledge import app as knowledge_app
from ubuntu_ai.cli.plan import plan
from ubuntu_ai.cli.tui import tui
from ubuntu_ai.cli.version import version_command

app = typer.Typer(
    name="ubuntu-ai",
    help="Ubuntu AI Assistant - Administração inteligente do Ubuntu",
    no_args_is_help=True,
)


@app.callback()
def main(
    ctx: typer.Context,
    debug: bool = typer.Option(
        False,
        "--debug",
        help="Exibe tracebacks completos para diagnóstico.",
    ),
) -> None:
    """Ubuntu AI Assistant."""

    ctx.obj = CLIContext(debug=debug)


app.add_typer(knowledge_app, name="knowledge")
app.command(name="diagnose-ai")(diagnose_ai)
app.command(name="doctor")(doctor)
app.command(name="benchmark")(benchmark)
app.command(name="plan")(plan)
app.command(name="tui")(tui)
app.command(name="version")(version_command)
