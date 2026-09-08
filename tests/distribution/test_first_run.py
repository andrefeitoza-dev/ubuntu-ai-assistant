from __future__ import annotations

from subprocess import CompletedProcess

import pytest

from ubuntu_ai.config import ConfigRepository
from ubuntu_ai.distribution.first_run import FirstRunSetup


def test_status_reports_missing_ollama() -> None:
    status = FirstRunSetup(executable="").status()

    assert not status.ready
    assert not status.ollama_available


def test_status_reports_ready_model(monkeypatch: pytest.MonkeyPatch) -> None:
    commands: list[tuple[str, ...]] = []

    def fake_run(command, **_kwargs):
        commands.append(tuple(command))
        return CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("ubuntu_ai.distribution.first_run.subprocess.run", fake_run)

    status = FirstRunSetup(executable="/usr/bin/ollama").status()

    assert status.ready
    assert commands == [
        ("/usr/bin/ollama", "list"),
        ("/usr/bin/ollama", "show", "qwen2.5:3b"),
    ]


def test_pull_model_never_uses_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    options: list[dict[str, object]] = []

    def fake_run(command, **kwargs):
        options.append(kwargs)
        return CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr("ubuntu_ai.distribution.first_run.subprocess.run", fake_run)

    result = FirstRunSetup(executable="/usr/bin/ollama").pull_model()

    assert result.returncode == 0
    assert options[0]["shell"] is False


def test_pull_model_requires_ollama() -> None:
    with pytest.raises(RuntimeError, match="Ollama não encontrado"):
        FirstRunSetup(executable="").pull_model()


def test_lists_installed_ollama_models(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    output = "NAME ID SIZE MODIFIED\nqwen2.5:3b abc 2 GB now\nllama3.2:3b def 2 GB now\n"
    monkeypatch.setattr(
        "ubuntu_ai.distribution.first_run.subprocess.run",
        lambda command, **kwargs: CompletedProcess(command, 0, output, ""),
    )
    setup = FirstRunSetup(
        executable="/usr/bin/ollama",
        config_repository=ConfigRepository(tmp_path / "config.toml"),
    )

    assert setup.list_models() == ("qwen2.5:3b", "llama3.2:3b")


def test_select_model_verifies_and_persists_choice(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    commands: list[tuple[str, ...]] = []
    listing = "NAME ID SIZE MODIFIED\nqwen2.5:3b abc 2 GB now\nllama3.2:3b def 2 GB now\n"

    def fake_run(command, **kwargs):
        commands.append(tuple(command))
        stdout = listing if command[-1] == "list" else ""
        return CompletedProcess(command, 0, stdout, "")

    monkeypatch.setattr("ubuntu_ai.distribution.first_run.subprocess.run", fake_run)
    repository = ConfigRepository(tmp_path / "config.toml")
    setup = FirstRunSetup(executable="/usr/bin/ollama", config_repository=repository)

    setup.select_model("llama3.2:3b")

    assert repository.load().ai.model == "llama3.2:3b"
    assert setup.model == "llama3.2:3b"
    assert commands == [
        ("/usr/bin/ollama", "list"),
        ("/usr/bin/ollama", "show", "llama3.2:3b"),
    ]


def test_select_model_rejects_uninstalled_choice(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    monkeypatch.setattr(
        "ubuntu_ai.distribution.first_run.subprocess.run",
        lambda command, **kwargs: CompletedProcess(command, 0, "NAME ID SIZE MODIFIED\n", ""),
    )
    setup = FirstRunSetup(
        executable="/usr/bin/ollama",
        config_repository=ConfigRepository(tmp_path / "config.toml"),
    )

    with pytest.raises(ValueError, match="modelo instalado"):
        setup.select_model("inventado:latest")
