from io import StringIO

from rich.console import Console

from ubuntu_ai.execution.models import (
    ExecutionResult,
    ExecutionStatus,
)
from ubuntu_ai.tui.renderer import TerminalRenderer


def make_renderer() -> tuple[TerminalRenderer, StringIO]:
    output = StringIO()

    renderer = TerminalRenderer(
        Console(
            file=output,
            force_terminal=False,
            width=120,
        )
    )

    return renderer, output


def test_results_displays_stdout() -> None:
    renderer, output = make_renderer()

    renderer.results(
        (
            ExecutionResult(
                status=ExecutionStatus.EXECUTED,
                message="Comando executado com sucesso.",
                command="pwd",
                return_code=0,
                stdout="/home/andre/projeto",
                duration=0.01,
            ),
        )
    )

    rendered = output.getvalue()

    assert "Resultados da execução" in rendered
    assert "pwd" in rendered
    assert "/home/andre/projeto" in rendered
    assert "Saída" in rendered


def test_results_displays_stderr() -> None:
    renderer, output = make_renderer()

    renderer.results(
        (
            ExecutionResult(
                status=ExecutionStatus.FAILED,
                message="O comando terminou com erro.",
                command="teste",
                return_code=1,
                stderr="permission denied",
                duration=0.02,
            ),
        )
    )

    rendered = output.getvalue()

    assert "permission denied" in rendered
    assert "Erro" in rendered
    assert "exit=1" in rendered


def test_results_keeps_summary_without_output() -> None:
    renderer, output = make_renderer()

    renderer.results(
        (
            ExecutionResult(
                status=ExecutionStatus.EXECUTED,
                message="Comando executado com sucesso.",
                command="true",
                return_code=0,
                duration=0.01,
            ),
        )
    )

    rendered = output.getvalue()

    assert "Resultados da execução" in rendered
    assert "true" in rendered
    assert "Comando executado com sucesso." in rendered