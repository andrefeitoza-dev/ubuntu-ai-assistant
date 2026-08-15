import platform

from rich.console import Console
from rich.table import Table

from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.version import __version__

console = Console()


def version_command() -> None:
    """Exibe informações da versão e do runtime configurado."""

    config = container.config()
    ollama_info = container.ollama_service().get_info()

    table = Table(title="Ubuntu AI Assistant")
    table.add_column("Item", style="cyan")
    table.add_column("Valor", style="green")
    table.add_row("Versão", __version__)
    table.add_row("Python", platform.python_version())
    table.add_row(
        "Ollama",
        ollama_info.version if ollama_info.available and ollama_info.version else "offline",
    )
    table.add_row("Modelo", config.ollama_model)
    console.print(table)
