from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.knowledge.exceptions import KnowledgeError

app = typer.Typer(help="Gerencia a base local de conhecimento.", no_args_is_help=True)
console = Console()


@app.command("add")
def add(
    path: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True),
    title: str | None = typer.Option(None, "--title", "-t"),
    tag: list[str] | None = typer.Option(None, "--tag"),
) -> None:
    """Importa um arquivo textual para a base local."""

    try:
        document = container.knowledge_engine().import_file(
            path, title=title, tags=tuple(tag or ())
        )
    except KnowledgeError as error:
        console.print(f"[red]Erro:[/red] {error}")
        raise typer.Exit(code=1) from error
    console.print(f"[green]Documento importado:[/green] {document.id} — {document.title}")


@app.command("list")
def list_documents(limit: int = typer.Option(50, min=1, max=1000)) -> None:
    """Lista documentos persistidos."""

    documents = container.knowledge_service().list_documents(limit=limit)
    table = Table(title="Knowledge Base")
    table.add_column("ID", no_wrap=True)
    table.add_column("Título")
    table.add_column("Origem")
    table.add_column("Tags")
    for document in documents:
        table.add_row(
            document.id,
            document.title,
            document.source.value,
            ", ".join(tag.name for tag in document.tags) or "-",
        )
    console.print(table)


@app.command("search")
def search(
    query: str = typer.Argument(...),
    limit: int = typer.Option(10, min=1, max=100),
) -> None:
    """Pesquisa documentos usando o índice FTS5."""

    try:
        results = container.knowledge_engine().search(query, limit=limit)
    except KnowledgeError as error:
        console.print(f"[red]Erro:[/red] {error}")
        raise typer.Exit(code=1) from error
    for result in results:
        console.print(f"\n[bold]{result.document.title}[/bold] [{result.score:.3f}]")
        console.print(result.excerpt)
        console.print(f"[dim]{result.document.id}[/dim]")
    if not results:
        console.print("Nenhum resultado encontrado.")


@app.command("remove")
def remove(document_id: str = typer.Argument(...)) -> None:
    """Remove um documento da base."""

    try:
        container.knowledge_service().delete_document(document_id)
    except KnowledgeError as error:
        console.print(f"[red]Erro:[/red] {error}")
        raise typer.Exit(code=1) from error
    console.print(f"[green]Documento removido:[/green] {document_id}")


@app.command("reindex")
def reindex(document_id: str | None = typer.Argument(None)) -> None:
    """Reconstrói trechos e índice de um documento ou de toda a base."""

    try:
        count = container.knowledge_engine().reindex(document_id)
    except (KnowledgeError, RuntimeError) as error:
        console.print(f"[red]Erro:[/red] {error}")
        raise typer.Exit(code=1) from error
    console.print(f"[green]Trechos indexados:[/green] {count}")
