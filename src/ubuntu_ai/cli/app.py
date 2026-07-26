import typer

from ubuntu_ai.cli.doctor import doctor
from ubuntu_ai.cli.knowledge import app as knowledge_app
from ubuntu_ai.cli.plan import plan

app = typer.Typer(
    name="ubuntu-ai",
    help="Ubuntu AI Assistant - Administração inteligente do Ubuntu",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Ubuntu AI Assistant."""


app.add_typer(knowledge_app, name="knowledge")
app.command(name="doctor")(doctor)
app.command(name="plan")(plan)
