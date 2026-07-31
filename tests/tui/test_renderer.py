from io import StringIO

from rich.console import Console

from ubuntu_ai.agent.models import AgentResult
from ubuntu_ai.agent_loop.models import LoopSnapshot, LoopState
from ubuntu_ai.tui.renderer import TerminalRenderer


def test_renderer_displays_pending_plan_and_status() -> None:
    output = StringIO()
    renderer = TerminalRenderer(
        Console(file=output, force_terminal=False, width=100)
    )
    snapshot = LoopSnapshot(
        goal="Instalar Docker",
        state=LoopState.WAITING_CONFIRMATION,
        iteration=1,
        pending_plan=AgentResult(success=True, message="Plano Docker"),
        records=(),
        events=(),
    )

    renderer.plan(snapshot)
    renderer.status(snapshot)

    rendered = output.getvalue()
    assert "Plano Docker" in rendered
    assert "Instalar Docker" in rendered
    assert "aguardando confirmação" in rendered
