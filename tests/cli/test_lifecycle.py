from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from ubuntu_ai.cli.app import app
from ubuntu_ai.distribution import LifecycleManager

runner = CliRunner()


def test_lifecycle_update_dry_run_does_not_execute(monkeypatch) -> None:
    executed: list[object] = []
    monkeypatch.setattr(
        "ubuntu_ai.cli.lifecycle._manager",
        lambda: LifecycleManager(uv_executable="/usr/bin/uv"),
    )
    monkeypatch.setattr(LifecycleManager, "execute", executed.append)

    result = runner.invoke(
        app,
        ["lifecycle", "update", "--version", "1.6.0", "--yes", "--dry-run"],
    )

    assert result.exit_code == 0
    assert "Simulação concluída" in result.stdout
    assert executed == []


def test_lifecycle_uninstall_dry_run_preserves_launcher(monkeypatch, tmp_path: Path) -> None:
    removed: list[Path] = []
    monkeypatch.setattr(
        "ubuntu_ai.cli.lifecycle._manager",
        lambda: LifecycleManager(uv_executable="/usr/bin/uv", home=tmp_path),
    )
    monkeypatch.setattr("ubuntu_ai.cli.lifecycle.uninstall_launcher", removed.append)

    result = runner.invoke(app, ["lifecycle", "uninstall", "--yes", "--dry-run"])

    assert result.exit_code == 0
    assert removed == []


def test_lifecycle_update_wheel_dry_run(monkeypatch, tmp_path: Path) -> None:
    wheel = tmp_path / "ubuntu_ai_assistant-1.6.0-py3-none-any.whl"
    wheel.write_bytes(b"wheel")
    monkeypatch.setattr(
        "ubuntu_ai.cli.lifecycle._manager",
        lambda: LifecycleManager(uv_executable="/usr/bin/uv"),
    )

    result = runner.invoke(
        app,
        ["lifecycle", "update", "--wheel", str(wheel), "--yes", "--dry-run"],
    )

    assert result.exit_code == 0
    assert "Atualizar a instalação isolada" in result.stdout
    assert "Simulação concluída" in result.stdout
