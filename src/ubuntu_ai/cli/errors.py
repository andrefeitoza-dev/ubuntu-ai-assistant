from rich.console import Console

_ERROR_HINTS = {
    "Ollama": (
        "Execute `ubuntu-ai doctor` e `ubuntu-ai diagnose-ai` para verificar o runtime local de IA."
    ),
    "plano": "Revise a solicitação ou execute `ubuntu-ai diagnose-ai`.",
    "execução": "Execute `ubuntu-ai doctor` e revise o plano antes de tentar novamente.",
}


def render_cli_error(
    console: Console,
    error: Exception,
    *,
    title: str = "Não foi possível concluir a operação.",
) -> None:
    """Exibe uma falha operacional sem despejar traceback no modo normal."""

    message = str(error).strip() or error.__class__.__name__
    console.print(f"[bold red]{title}[/bold red]")
    console.print(f"[red]Detalhes:[/red] {message}")

    for keyword, hint in _ERROR_HINTS.items():
        if keyword.casefold() in message.casefold():
            console.print(f"[yellow]Sugestão:[/yellow] {hint}")
            break
    else:
        console.print(
            "[yellow]Sugestão:[/yellow] Execute `ubuntu-ai doctor` para revisar o ambiente."
        )
