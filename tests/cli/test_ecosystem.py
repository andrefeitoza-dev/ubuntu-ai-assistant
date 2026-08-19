from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from ubuntu_ai.cli.app import app

runner = CliRunner()


def test_ecosystem_exports_portable_config(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "state"))
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    destination = tmp_path / "portable.toml"

    result = runner.invoke(app, ["ecosystem", "export-config", str(destination)])

    assert result.exit_code == 0
    assert destination.is_file()
    assert "[paths]" not in destination.read_text(encoding="utf-8")


def test_ecosystem_creates_restrictive_agent_profiles(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))

    result = runner.invoke(app, ["ecosystem", "profiles"])

    assert result.exit_code == 0
    assert "system-readonly" in result.stdout
    assert (tmp_path / "config" / "ubuntu-ai" / "agent-profiles.json").is_file()
