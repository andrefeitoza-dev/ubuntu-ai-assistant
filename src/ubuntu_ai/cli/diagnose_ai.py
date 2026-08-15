import typer
from rich.console import Console
from rich.table import Table

from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.diagnostics.models import DiagnosticStatus

console = Console()

_STATUS_LABELS = {
    DiagnosticStatus.PASSED: "[green]OK[/green]",
    DiagnosticStatus.WARNING: "[yellow]AVISO[/yellow]",
    DiagnosticStatus.FAILED: "[red]FALHA[/red]",
}


def diagnose_ai(
    request: str = typer.Option(
        "mostrar o diretório atual",
        "--request",
        "-r",
        help="Solicitação usada no teste de planejamento estruturado.",
    ),
) -> None:
    """Diagnostica conexão, modelo, prompt e geração estruturada."""

    service = container.ai_diagnostics_service()

    with console.status("[bold cyan]Executando diagnóstico de IA...[/bold cyan]"):
        report = service.run(request)

    table = Table(title="Ubuntu AI — Diagnóstico do Runtime de IA")
    table.add_column("Verificação", style="cyan", no_wrap=True)
    table.add_column("Estado", no_wrap=True)
    table.add_column("Tempo", justify="right")
    table.add_column("Resultado")

    for check in report.checks:
        duration = f"{check.duration_seconds:.2f}s" if check.duration_seconds is not None else "—"
        table.add_row(
            check.name,
            _STATUS_LABELS[check.status],
            duration,
            check.message,
        )

    console.print(table)
    console.print(f"[dim]Provedor:[/dim] {report.provider}")
    console.print(f"[dim]Modelo:[/dim] {report.model}")

    for check in report.checks:
        if not check.details:
            continue
        console.print(f"\n[bold]{check.name}[/bold]")
        for key, value in check.details.items():
            console.print(f"  [dim]{key}:[/dim] {value}")

    if not report.successful:
        raise typer.Exit(code=1)
