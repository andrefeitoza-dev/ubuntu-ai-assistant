from pathlib import Path

from ubuntu_ai.knowledge.models import KnowledgeDocument, KnowledgeSource, KnowledgeTag
from ubuntu_ai.knowledge.sqlite_repository import SQLiteKnowledgeRepository


def make_document(title: str, content: str, *tags: str) -> KnowledgeDocument:
    return KnowledgeDocument.create(
        title=title,
        content=content,
        source=KnowledgeSource.FILE,
        tags=tuple(KnowledgeTag(tag) for tag in tags),
    )


def test_sqlite_repository_persists_document(tmp_path: Path) -> None:
    database_path = tmp_path / "knowledge.db"
    repository = SQLiteKnowledgeRepository(database_path)
    document = make_document("Docker", "Docker instala containers no Ubuntu.", "ubuntu")

    repository.add_document(document)
    reopened = SQLiteKnowledgeRepository(database_path)

    assert reopened.get_document(document.id) == document
    assert reopened.document_exists(document.id)


def test_sqlite_repository_searches_chunks_with_fts5(tmp_path: Path) -> None:
    repository = SQLiteKnowledgeRepository(tmp_path / "knowledge.db")
    docker = make_document("Docker", "Use apt install docker.io para instalar Docker.")
    git = make_document("Git", "Use git status para verificar o repositório.")
    repository.add_document(docker)
    repository.add_document(git)

    results = repository.search("docker instalar")

    assert results
    assert results[0].document.id == docker.id
    assert results[0].matched_chunks


def test_sqlite_repository_updates_and_reindexes(tmp_path: Path) -> None:
    repository = SQLiteKnowledgeRepository(tmp_path / "knowledge.db")
    document = make_document("Manual", "Conteúdo antigo sobre rede.")
    repository.add_document(document)

    updated = document.with_updates(content="Conteúdo novo sobre firewall UFW.")
    repository.update_document(updated)

    assert repository.search("firewall")[0].document.id == document.id
    assert repository.search("antigo") == ()
    assert repository.reindex_document(document.id) >= 1


def test_sqlite_repository_finds_related_by_tags_and_title(tmp_path: Path) -> None:
    repository = SQLiteKnowledgeRepository(tmp_path / "knowledge.db")
    source = make_document("Docker Ubuntu", "Instalação do Docker.", "containers")
    related = make_document("Containers", "Docker e Podman executam containers.", "containers")
    repository.add_document(source)
    repository.add_document(related)

    results = repository.find_related(source.id)

    assert any(result.document.id == related.id for result in results)


def test_sqlite_repository_deletes_document(tmp_path: Path) -> None:
    repository = SQLiteKnowledgeRepository(tmp_path / "knowledge.db")
    document = make_document("Arquivo", "Conteúdo removível.")
    repository.add_document(document)

    assert repository.delete_document(document.id) is True
    assert repository.get_document(document.id) is None
    assert repository.search("removível") == ()
