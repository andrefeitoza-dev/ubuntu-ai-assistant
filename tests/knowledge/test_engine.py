from pathlib import Path

from ubuntu_ai.knowledge.engine import KnowledgeEngine
from ubuntu_ai.knowledge.service import KnowledgeService
from ubuntu_ai.knowledge.sqlite_repository import SQLiteKnowledgeRepository


def test_engine_imports_file_and_searches(tmp_path: Path) -> None:
    repository = SQLiteKnowledgeRepository(tmp_path / "knowledge.db")
    engine = KnowledgeEngine(KnowledgeService(repository))
    file_path = tmp_path / "ufw.md"
    file_path.write_text("Use sudo ufw enable para ativar o firewall.", encoding="utf-8")

    document = engine.import_file(file_path, tags=("security",))
    results = engine.search("firewall")

    assert document.source_reference == str(file_path.resolve())
    assert results[0].document.id == document.id


def test_engine_reindexes_all_documents(tmp_path: Path) -> None:
    repository = SQLiteKnowledgeRepository(tmp_path / "knowledge.db")
    engine = KnowledgeEngine(KnowledgeService(repository))
    engine.add_text(title="APT", content="apt update atualiza os índices.")

    assert engine.reindex() >= 1
