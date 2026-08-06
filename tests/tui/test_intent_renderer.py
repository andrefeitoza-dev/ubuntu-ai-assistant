from io import StringIO

from rich.console import Console

from ubuntu_ai.intent.models import Intent, IntentCategory, IntentGoal
from ubuntu_ai.tui.renderer import TerminalRenderer


def test_renderer_displays_intent() -> None:
    output = StringIO()
    renderer = TerminalRenderer(
        Console(file=output, force_terminal=False, width=100)
    )
    intent = Intent(
        request="mostrar diretório",
        category=IntentCategory.QUERY,
        goal=IntentGoal.INSPECT,
        confidence=0.9,
    )

    renderer.intent(intent)

    rendered = output.getvalue()
    assert "Intenção detectada" in rendered
    assert "query" in rendered
    assert "inspect" in rendered
    assert "90%" in rendered
