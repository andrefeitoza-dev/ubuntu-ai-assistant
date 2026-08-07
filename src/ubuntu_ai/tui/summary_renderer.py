from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.table import Table


@dataclass(frozen=True, slots=True)
class ExecutionSummary:
    status: str
    operations: int = 0
    duration_seconds: float = 0.0
    message: str = ""


class SummaryRenderer:
    """Renderiza o fechamento de uma execução."""

    def __init__(self, console: Console) -> None:
        self._console = console

    def render(self, summary: ExecutionSummary) -> None:
        table = Table(title="Resumo da execução", show_header=False)
        table.add_column("Campo", style="bold")
        table.add_column("Valor")

        table.add_row("Status", summary.status)
        table.add_row("Operações", str(summary.operations))
        table.add_row(
            "Tempo",
            f"{summary.duration_seconds:.2f}s",
        )

        if summary.message:
            table.add_row("Detalhes", summary.message)

        self._console.print(table)
