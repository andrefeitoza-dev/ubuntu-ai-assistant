from io import StringIO

from rich.console import Console

from ubuntu_ai.benchmark import BenchmarkService
from ubuntu_ai.tui.models import TerminalAppConfig
from ubuntu_ai.tui.renderer import TerminalRenderer


def test_renderer_displays_benchmark_summary() -> None:
    output = StringIO()
    renderer = TerminalRenderer(Console(file=output, force_terminal=False, width=100))
    service = BenchmarkService()
    service.record("planner", 0.25)
    service.record("pipeline", 0.50)

    renderer.benchmark(service.report())

    rendered = output.getvalue()
    assert "Desempenho" in rendered
    assert "planner" in rendered
    assert "pipeline" in rendered
    assert "Total" in rendered


def test_terminal_config_rejects_empty_spinner_text() -> None:
    try:
        TerminalAppConfig(spinner_text="   ")
    except ValueError as error:
        assert "spinner_text" in str(error)
    else:
        raise AssertionError("TerminalAppConfig deveria rejeitar spinner vazio.")
