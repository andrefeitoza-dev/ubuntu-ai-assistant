from __future__ import annotations

from rich.console import Console
from rich.prompt import Confirm

from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.tui.plan_renderer import PlanRenderer


class ConfirmationRenderer:
    """Apresenta o plano antes de solicitar confirmação."""

    def __init__(self, console: Console) -> None:
        self._console = console
        self._plan_renderer = PlanRenderer(console)

    def confirm(self, plan: Plan) -> bool:
        self._console.rule("[bold]Confirmação")
        self._plan_renderer.render(plan)
        return Confirm.ask(
            "Executar este plano?",
            default=False,
            console=self._console,
        )
