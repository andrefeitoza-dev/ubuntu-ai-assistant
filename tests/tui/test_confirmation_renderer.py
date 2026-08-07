from io import StringIO

from rich.console import Console

from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.tui.confirmation_renderer import ConfirmationRenderer


def test_confirmation_renderer_displays_confirmation_title(monkeypatch) -> None:
    output = StringIO()
    console = Console(
        file=output,
        force_terminal=False,
        width=100,
    )

    monkeypatch.setattr(
        "ubuntu_ai.tui.confirmation_renderer.Confirm.ask",
        lambda *args, **kwargs: True,
    )

    plan = Plan(
        goal="Teste",
        estimated_seconds=10,
        risk=RiskLevel.LOW,
    )

    accepted = ConfirmationRenderer(console).confirm(plan)

    assert accepted
    assert "Confirmação" in output.getvalue()
