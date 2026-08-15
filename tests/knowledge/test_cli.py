from pathlib import Path

from typer.testing import CliRunner

from ubuntu_ai.cli.app import app
from ubuntu_ai.container.bootstrap import container
from ubuntu_ai.knowledge.sqlite_repository import SQLiteKnowledgeRepository

runner = CliRunner()


def configure_repository(tmp_path: Path) -> None:
    container.register_knowledge_repository(SQLiteKnowledgeRepository(tmp_path / "knowledge.db"))


def test_cli_add_list_search_and_remove(tmp_path: Path) -> None:
    configure_repository(tmp_path)
    path = tmp_path / "docker.md"
    path.write_text("Docker executa containers no Ubuntu.", encoding="utf-8")

    added = runner.invoke(app, ["knowledge", "add", str(path), "--tag", "ubuntu"])
    assert added.exit_code == 0
    document_id = added.stdout.split(":", maxsplit=1)[1].split("—", maxsplit=1)[0].strip()

    listed = runner.invoke(app, ["knowledge", "list"])
    searched = runner.invoke(app, ["knowledge", "search", "containers"])
    removed = runner.invoke(app, ["knowledge", "remove", document_id])

    assert listed.exit_code == 0
    assert "docker" in listed.stdout.lower()
    assert searched.exit_code == 0
    assert "Docker" in searched.stdout
    assert removed.exit_code == 0
