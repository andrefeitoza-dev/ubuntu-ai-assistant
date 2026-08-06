from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.intent.presenter import IntentPresenter

console = Console()


def intent(
    request: str = typer.Argument(..., help="Solicitação a ser interpretada."),
) -> None:
    """Interpreta uma solicitação sem gerar ou executar um plano."""

    analyzed = container.intent_engine().interpret(request)
    view = IntentPresenter().present(analyzed)

    table = Table(title="Ubuntu AI — Intent")
    table.add_column("Campo", style="bold cyan")
    table.add_column("Valor")
    table.add_row("Solicitação", view.request)
    table.add_row("Categoria", view.category)
    table.add_row("Objetivo", view.goal)
    table.add_row("Confiança", view.confidence_percent)
    table.add_row("Entidades", view.entities)
    table.add_row("Confirmação", view.requires_confirmation)
    console.print(table)
