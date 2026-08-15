from __future__ import annotations

from rich.console import Console
from rich.table import Table

from ubuntu_ai.domain.plan import Plan


class PlanRenderer:
    """Renderiza plano de forma compacta e orientada à decisão."""

    def __init__(self, console: Console) -> None:
        self._console = console

    def render(self, plan: Plan) -> None:
        summary = Table(show_header=False, box=None)
        summary.add_column("Campo", style="bold")
        summary.add_column("Valor")

        summary.add_row("Objetivo", plan.goal)
        summary.add_row("Risco", plan.risk.value)
        summary.add_row(
            "Tempo estimado",
            f"{plan.estimated_seconds}s",
        )
        summary.add_row("Etapas", str(len(plan.steps)))

        self._console.print(summary)

        steps = Table(title="Etapas do plano")
        steps.add_column("#", justify="right")
        steps.add_column("Etapa")
        steps.add_column("Descrição")
        steps.add_column("Ferramenta")

        for index, step in enumerate(plan.steps, start=1):
            steps.add_row(
                str(index),
                step.title,
                step.description,
                step.tool_name or "shell",
            )

        self._console.print(steps)
