from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "integrations" / "vscode"


def test_vscode_manifest_registers_only_expected_commands() -> None:
    manifest = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    commands = {entry["command"] for entry in manifest["contributes"]["commands"]}

    assert commands == {
        "ubuntuAI.openGui",
        "ubuntuAI.doctor",
        "ubuntuAI.health",
        "ubuntuAI.plan",
        "ubuntuAI.preview",
        "ubuntuAI.profiles",
    }


def test_vscode_extension_never_uses_shell_execution() -> None:
    source = (ROOT / "extension.js").read_text(encoding="utf-8")

    assert "shell: false" in source
    assert "shell: true" not in source
    assert "exec(" not in source
    assert "eval(" not in source


def test_vscode_action_preview_is_always_dry_run() -> None:
    source = (ROOT / "extension.js").read_text(encoding="utf-8")

    assert 'safeCommand(["run", "--dry-run", request]' in source
    assert 'safeCommand(["run", request]' not in source


def test_vscode_executables_are_restricted_by_name() -> None:
    source = (ROOT / "extension.js").read_text(encoding="utf-8")

    assert 'configuredExecutable("executable", "ubuntu-ai")' in source
    assert 'configuredExecutable("guiExecutable", "ubuntu-ai-gui")' in source
