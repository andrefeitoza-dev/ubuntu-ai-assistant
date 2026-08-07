from io import StringIO

from rich.console import Console

from ubuntu_ai.tui.summary_renderer import (
    ExecutionSummary,
    SummaryRenderer,
)


def test_summary_renderer_displays_execution_summary() -> None:
    output = StringIO()
    renderer = SummaryRenderer(
        Console(file=output, force_terminal=False)
    )

    renderer.render(
        ExecutionSummary(
            status="SUCCESS",
            operations=4,
            duration_seconds=1.25,
            message="Tudo certo",
        )
    )

    rendered = output.getvalue()
    assert "Resumo da execução" in rendered
    assert "SUCCESS" in rendered
    assert "Tudo certo" in rendered
