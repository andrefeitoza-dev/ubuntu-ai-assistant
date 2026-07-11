from rich.console import Console
from rich.table import Table

from ubuntu_ai.services.ollama import OllamaService
from ubuntu_ai.services.system import SystemService

console = Console()


def doctor() -> None:
    """Verifica se o ambiente está pronto para usar o Ubuntu AI Assistant."""

    system_service = SystemService()
    ollama_service = OllamaService()

    system_info = system_service.get_info()
    ollama_info = ollama_service.get_info()

    table = Table(title="Ubuntu AI Assistant - Health Check")

    table.add_column("Item", style="cyan")
    table.add_column("Valor", style="green")

    table.add_row("Python", system_info.python_version)
    table.add_row("Sistema", system_info.operating_system)
    table.add_row("Arquitetura", system_info.architecture)
    table.add_row("CPU lógica", str(system_info.cpu_cores))
    table.add_row("RAM total", f"{system_info.ram_total_gb} GiB")
    table.add_row("RAM disponível", f"{system_info.ram_available_gb} GiB")
    table.add_row(
        "Git",
        "Instalado" if system_info.git_installed else "Não encontrado",
    )

    if ollama_info.available:
        table.add_row("Ollama", f"Online — versão {ollama_info.version}")
        table.add_row(
            "Modelos",
            ", ".join(ollama_info.models) if ollama_info.models else "Nenhum instalado",
        )
    else:
        table.add_row("Ollama", "Offline ou não encontrado")
        table.add_row("Modelos", "Indisponível")

    console.print(table)
