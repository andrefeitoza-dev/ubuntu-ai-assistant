from __future__ import annotations

from subprocess import CompletedProcess

import pytest

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
