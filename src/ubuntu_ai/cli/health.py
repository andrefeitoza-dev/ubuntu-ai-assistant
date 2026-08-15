from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ubuntu_ai.container.bootstrap import container

console = Console()


def health() -> None:
    """Exibe prontidão dos componentes e métricas do runtime."""

    runtime = container.application_runtime()
    report = runtime.health()

    table = Table(title="Saúde da aplicação")
    table.add_column("Componente")
    table.add_column("Status")
    table.add_column("Detalhes")

    for component in report.components:
        table.add_row(
            component.name,
            component.status.value,
            component.message or "—",
        )

    console.print(table)

    telemetry = runtime.telemetry()
    if telemetry.metrics:
        metrics = Table(title="Telemetria do runtime")
        metrics.add_column("Operação")
        metrics.add_column("Chamadas", justify="right")
        metrics.add_column("Falhas", justify="right")
        metrics.add_column("Média", justify="right")

        for metric in telemetry.metrics:
            metrics.add_row(
                metric.operation,
                str(metric.calls),
                str(metric.failures),
                f"{metric.average_duration:.4f}s",
            )

        console.print(metrics)

    if not report.ready:
        raise typer.Exit(code=1)
