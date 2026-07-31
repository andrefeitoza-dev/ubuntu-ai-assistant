from importlib import import_module
from types import SimpleNamespace

from typer.testing import CliRunner

from ubuntu_ai.cli.app import app

runner = CliRunner()
module = import_module("ubuntu_ai.cli.version")


def test_version_command_displays_release_and_runtime(monkeypatch) -> None:
    monkeypatch.setattr(module, "__version__", "0.6.0rc1")
    monkeypatch.setattr(
        module.container,
        "config",
        lambda: SimpleNamespace(ollama_model="qwen2.5:3b"),
    )
    monkeypatch.setattr(
        module.container,
        "ollama_service",
        lambda: SimpleNamespace(
            get_info=lambda: SimpleNamespace(available=True, version="0.24.0")
        ),
    )

    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert "0.6.0rc1" in result.stdout
    assert "qwen2.5:3b" in result.stdout
    assert "0.24.0" in result.stdout
