from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ubuntu_ai.distribution import LifecycleManager, LifecyclePlan
from ubuntu_ai.gui.launcher_installer import install as install_launcher
from ubuntu_ai.gui.launcher_installer import uninstall as uninstall_launcher

app = typer.Typer(help="Instalação, atualização e remoção controladas.")
console = Console()


def _manager() -> LifecycleManager:
    return LifecycleManager()


def _confirm(plan: LifecyclePlan, *, yes: bool) -> None:
    console.print(f"[bold]{plan.description}[/bold]")
    console.print("Comando:", " ".join(plan.command))
    if not yes and not typer.confirm("Deseja continuar?"):
        raise typer.Abort()


def _run(plan: LifecyclePlan, *, yes: bool, dry_run: bool) -> None:
    _confirm(plan, yes=yes)
    if dry_run:
        console.print("[yellow]Simulação concluída; nenhuma alteração foi feita.[/yellow]")
        return
    result = LifecycleManager.execute(plan)
    if result.stdout.strip():
        console.print(result.stdout.rstrip())
    if not result.success:
        detail = result.stderr.strip() or f"código de saída {result.return_code}"
        raise typer.BadParameter(f"Operação não concluída: {detail}")


@app.command("status")
def status_command() -> None:
    """Mostra a integridade da instalação atual."""

    status = _manager().status()
    table = Table(title="Ubuntu AI — Ciclo de vida")
    table.add_column("Item")
    table.add_column("Estado")
    table.add_row("Versão", status.version or "não instalada")
    table.add_row("CLI", "OK" if status.command_available else "ausente")
    table.add_row("GUI", "OK" if status.gui_available else "ausente")
    table.add_row("Launcher", "OK" if status.launcher_installed else "ausente")
    table.add_row("Entrada desktop", "OK" if status.desktop_installed else "ausente")
    table.add_row("Ícone", "OK" if status.icon_installed else "ausente")
    console.print(table)
    console.print("Dados preservados em:")
    for directory in status.preserved_directories:
        console.print(f"- {directory}")


@app.command("install")
def install_command(
    wheel: Path | None = typer.Option(None, help="Caminho absoluto de um wheel validado."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirma a operação."),
    dry_run: bool = typer.Option(False, help="Mostra o plano sem executá-lo."),
) -> None:
    """Instala o pacote isoladamente e recria o launcher."""

    manager = _manager()
    _run(manager.install_plan(str(wheel) if wheel else None), yes=yes, dry_run=dry_run)
    if not dry_run:
        install_launcher(Path.home())


@app.command("update")
def update_command(
    version: str | None = typer.Option(None, help="Versão exata desejada."),
    wheel: Path | None = typer.Option(None, help="Wheel absoluto validado para atualização."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirma a operação."),
    dry_run: bool = typer.Option(False, help="Mostra o plano sem executá-lo."),
) -> None:
    """Atualiza o pacote sem apagar dados do usuário."""

    manager = _manager()
    _run(
        manager.update_plan(version, str(wheel) if wheel else None),
        yes=yes,
        dry_run=dry_run,
    )
    if not dry_run:
        install_launcher(Path.home())


@app.command("uninstall")
def uninstall_command(
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirma a operação."),
    dry_run: bool = typer.Option(False, help="Mostra o plano sem executá-lo."),
) -> None:
    """Remove pacote e launcher, preservando dados pessoais."""

    manager = _manager()
    plan = manager.uninstall_plan()
    _confirm(plan, yes=yes)
    if dry_run:
        console.print("[yellow]Simulação concluída; nenhuma alteração foi feita.[/yellow]")
        return
    uninstall_launcher(Path.home())
    result = manager.execute(plan)
    if not result.success:
        detail = result.stderr.strip() or f"código de saída {result.return_code}"
        raise typer.BadParameter(f"Pacote não removido: {detail}")
    console.print("Configurações, dados e histórico foram preservados.")
