from pathlib import Path

from ubuntu_ai.agent.context import ContextProvider


def test_context_provider_detects_current_directory(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.chdir(tmp_path)

    context = ContextProvider().get_context()

    assert context.working_directory == tmp_path
    assert context.project_name is None
    assert context.operating_system


def test_context_provider_detects_python_project(
    monkeypatch,
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text(
        "[project]\nname = 'example'\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    context = ContextProvider().get_context()

    assert context.working_directory == tmp_path
    assert context.project_name == tmp_path.name