from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

console = Console()


def examples() -> None:
    """Exibe exemplos de utilização do Ubuntu AI Assistant."""

    console.print(
        Panel.fit(
            """[bold cyan]Exemplos rápidos[/bold cyan]

[bold]Sistema[/bold]

ubuntu-ai run "mostre uso de disco"
ubuntu-ai run "memória"
ubuntu-ai run "cpu"
ubuntu-ai run "quem sou eu"
ubuntu-ai run "kernel"

[bold]Arquivos[/bold]

ubuntu-ai run "onde estou"
ubuntu-ai run "listar arquivos"

[bold]Rede[/bold]

ubuntu-ai run "meu ip"
ubuntu-ai run "wifi"

[bold]Diagnóstico[/bold]

ubuntu-ai doctor
ubuntu-ai health
ubuntu-ai benchmark

[bold]Modo Interativo[/bold]

ubuntu-ai shell
ubuntu-ai tui
""",
            title="Ubuntu AI Assistant",
            border_style="cyan",
        )
    )
