from io import StringIO

from rich.console import Console

from ubuntu_ai.tui.status_renderer import StatusRenderer


def test_status_renderer_displays_success_message() -> None:
    output = StringIO()
    renderer = StatusRenderer(
        Console(file=output, force_terminal=False)
    )

    renderer.success("Operação concluída")

    rendered = output.getvalue()
    assert "Concluído" in rendered
    assert "Operação concluída" in rendered
