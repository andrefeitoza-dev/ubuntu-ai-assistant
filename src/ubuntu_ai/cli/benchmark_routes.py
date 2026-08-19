from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from ubuntu_ai.container.bootstrap import container

console = Console()


def benchmark_routes(
    include_chat: bool = typer.Option(
        False,
        "--include-chat",
        help="Inclui duas gerações reais pelo Ollama.",
    ),
    question: str = typer.Option(
        "Explique em uma frase o que é Linux.",
        "--question",
        help="Pergunta usada para medir a conversa.",
    ),
) -> None:
    """Compara as rotas local, ação segura e IA conversacional."""

    router = container.interaction_router()
    measurements = [
        ("Local", router.route("que dia é hoje?").duration, "sem Ollama"),
        ("Ação segura", router.route("qual a memória?").duration, "sem Ollama"),
        ("Roteamento chat", router.route(question).duration, "classificação"),
    ]

    if include_chat:
        chat = container.chat_service()
        first = chat.ask(question)
        second = chat.ask("Resuma a resposta anterior em uma frase.")
        measurements.extend(
            (
                ("IA — primeira medição", first.duration, first.model),
                ("IA — modelo aquecido", second.duration, second.model),
            )
        )

    table = Table(title="Ubuntu AI — Benchmark das rotas")
    table.add_column("Rota")
    table.add_column("Tempo", justify="right")
    table.add_column("Observação")
    for name, duration, note in measurements:
        table.add_row(name, _duration(duration), note)
    console.print(table)

    if include_chat:
        console.print(
            "[dim]A primeira medição representa cold start somente quando o modelo "
            "ainda não estava carregado.[/dim]"
        )


def _duration(seconds: float) -> str:
    if seconds < 0.001:
        return f"{seconds * 1_000_000:.0f} µs"
    if seconds < 1.0:
        return f"{seconds * 1000:.1f} ms"
    return f"{seconds:.2f} s"
