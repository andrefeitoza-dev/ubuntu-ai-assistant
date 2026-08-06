from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ubuntu_ai.container.bootstrap import container

console = Console()


def benchmark(
    request: str = typer.Option(
        "mostrar o diretório atual",
        "--request",
        "-r",
        help="Solicitação usada na medição do pipeline.",
    ),
) -> None:
    """Executa e exibe um benchmark do pipeline local."""

    service = container.benchmark_service()
    service.clear()
    try:
        result = container.execution_pipeline().run(request)
    except (RuntimeError, ValueError) as error:
        console.print(f"[red]Erro:[/red] {error}")
        raise typer.Exit(code=1) from error

    report = service.report()
    if result.intent is not None:
        console.print(
            f"[bold cyan]Intenção:[/bold cyan] "
            f"{result.intent.category.value}/{result.intent.goal.value} "
            f"({result.intent.confidence:.0%})"
        )
    table = Table(title="Ubuntu AI — Benchmark")
    table.add_column("Operação")
    table.add_column("Tempo", justify="right")
    table.add_column("Estado")
    for record in report.records:
        table.add_row(
            record.operation,
            f"{record.duration:.4f}s",
            "OK" if record.success else "FALHA",
        )
    table.add_section()
    table.add_row("Total", f"{report.total_duration:.4f}s", "")
    table.add_row("Média", f"{report.average_duration:.4f}s", "")
    console.print(table)
