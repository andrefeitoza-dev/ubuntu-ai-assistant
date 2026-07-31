import typer

from ubuntu_ai.container.bootstrap import container


def tui() -> None:
    """Abre a interface interativa do Ubuntu AI no terminal."""

    try:
        container.terminal_app().run()
    except (KeyboardInterrupt, EOFError):
        raise typer.Exit(code=0) from None
