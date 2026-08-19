from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ubuntu_ai.agents import AgentProfileRepository, default_agent_profiles
from ubuntu_ai.config import ConfigTransferService, default_config_directory
from ubuntu_ai.plugins import PluginCatalog, PluginTrustStore

app = typer.Typer(help="Configurações portáteis, perfis e catálogo de plugins.")
console = Console()


def _trust_store() -> PluginTrustStore:
    return PluginTrustStore(default_config_directory() / "trusted-plugins.json")


@app.command("export-config")
def export_config(destination: Path) -> None:
    """Exporta configuração portátil sem segredos ou caminhos locais."""

    path = ConfigTransferService().export_file(destination)
    console.print(f"Configuração exportada: {path}")


@app.command("import-config")
def import_config(
    source: Path,
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirma a substituição."),
) -> None:
    """Valida e importa configuração, preservando os caminhos locais."""

    if not yes and not typer.confirm("Substituir a configuração atual?"):
        raise typer.Abort()
    ConfigTransferService().import_file(source)
    console.print("Configuração importada e validada.")


@app.command("profiles")
def profiles() -> None:
    """Lista e persiste os perfis restritivos padrão."""

    path = default_config_directory() / "agent-profiles.json"
    repository = AgentProfileRepository(path)
    if not repository.load():
        repository.save(default_agent_profiles())
    table = Table(title="Perfis de agentes")
    table.add_column("Perfil")
    table.add_column("Agente")
    table.add_column("Ações")
    table.add_column("Tentativas")
    for profile in repository.load():
        table.add_row(
            profile.name,
            profile.kind.value,
            str(profile.max_actions),
            str(profile.max_attempts),
        )
    console.print(table)
    console.print(f"Catálogo: {path}")


@app.command("scan-plugins")
def scan_plugins(directory: Path) -> None:
    """Inspeciona plugins sem importar código."""

    entries = PluginCatalog(_trust_store()).scan(directory)
    table = Table(title="Catálogo local de plugins")
    table.add_column("Plugin")
    table.add_column("Versão")
    table.add_column("Estado")
    table.add_column("Motivo")
    for entry in entries:
        table.add_row(entry.name, entry.version or "-", entry.status.value, entry.reason)
    console.print(table)


@app.command("trust-plugin")
def trust_plugin(
    manifest: Path,
    yes: bool = typer.Option(False, "--yes", "-y", help="Confirma a confiança."),
) -> None:
    """Aprova explicitamente o conteúdo atual de um plugin."""

    if not yes and not typer.confirm(f"Confiar no plugin descrito por {manifest}?"):
        raise typer.Abort()
    fingerprint = _trust_store().approve(manifest)
    console.print(f"Plugin aprovado: {fingerprint}")
