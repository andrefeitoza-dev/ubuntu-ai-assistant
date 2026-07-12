import typer

from ubuntu_ai.cli.doctor import doctor
from ubuntu_ai.cli.plan import plan

app = typer.Typer(
    name="ubuntu-ai",
    help="Ubuntu AI Assistant - Administração inteligente do Ubuntu",
    no_args_is_help=True,
)


@app.callback()
def main() -> None:
    """Ubuntu AI Assistant."""


app.command(name="doctor")(doctor)
app.command(name="plan")(plan)
