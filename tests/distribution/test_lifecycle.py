from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from ubuntu_ai.distribution import LifecycleManager, LifecycleOperation


def manager(tmp_path: Path) -> LifecycleManager:
    return LifecycleManager(uv_executable="/usr/bin/uv", home=tmp_path)


def test_install_from_registry_uses_isolated_uv_tool(tmp_path: Path) -> None:
    plan = manager(tmp_path).install_plan()

    assert plan.operation is LifecycleOperation.INSTALL
    assert plan.command == ("/usr/bin/uv", "tool", "install", "ubuntu-ai-assistant")


def test_install_accepts_only_absolute_existing_project_wheel(tmp_path: Path) -> None:
    wheel = tmp_path / "ubuntu_ai_assistant-1.6.0-py3-none-any.whl"
    wheel.write_bytes(b"wheel")

    plan = manager(tmp_path).install_plan(str(wheel))

    assert plan.command[-1] == str(wheel)


@pytest.mark.parametrize(
    "source",
    ("relative.whl", "/tmp/other-1.0.0-py3-none-any.whl", ""),
)
def test_install_rejects_untrusted_source(tmp_path: Path, source: str) -> None:
    with pytest.raises(ValueError):
        manager(tmp_path).install_plan(source)


def test_update_accepts_an_exact_validated_version(tmp_path: Path) -> None:
    plan = manager(tmp_path).update_plan("1.6.0")

    assert plan.operation is LifecycleOperation.UPDATE
    assert plan.command == (
        "/usr/bin/uv",
        "tool",
        "install",
        "--force",
        "ubuntu-ai-assistant==1.6.0",
    )


def test_update_accepts_local_project_wheel(tmp_path: Path) -> None:
    wheel = tmp_path / "ubuntu_ai_assistant-1.6.0-py3-none-any.whl"
    wheel.write_bytes(b"wheel")

    plan = manager(tmp_path).update_plan(wheel=str(wheel))

    assert plan.command == (
        "/usr/bin/uv",
        "tool",
        "install",
        "--force",
        str(wheel),
    )


def test_update_rejects_version_and_wheel_together(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="nunca os dois"):
        manager(tmp_path).update_plan("1.6.0", "/tmp/package.whl")


@pytest.mark.parametrize("value", ("latest; rm -rf /", "v1.6", "", "1.6"))
def test_update_rejects_invalid_version(tmp_path: Path, value: str) -> None:
    with pytest.raises(ValueError, match="Versão inválida"):
        manager(tmp_path).update_plan(value)


def test_uninstall_preserves_user_directories(tmp_path: Path, monkeypatch) -> None:
    config = tmp_path / "config"
    data = tmp_path / "data"
    state = tmp_path / "state"
    cache = tmp_path / "cache"
    for directory in (config, data, state, cache):
        directory.mkdir()
        (directory / "keep").write_text("preserved", encoding="utf-8")

    monkeypatch.setattr(
        LifecycleManager,
        "preserved_directories",
        staticmethod(lambda: (config, data, state, cache)),
    )
    plan = manager(tmp_path).uninstall_plan()

    assert plan.command == ("/usr/bin/uv", "tool", "uninstall", "ubuntu-ai-assistant")
    assert all(
        (directory / "keep").is_file() for directory in manager(tmp_path).preserved_directories()
    )


def test_execute_never_uses_shell(monkeypatch, tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured.update(kwargs)
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("ubuntu_ai.distribution.lifecycle.subprocess.run", fake_run)
    plan = manager(tmp_path).update_plan("1.6.0")

    result = LifecycleManager.execute(plan)

    assert result.success
    assert captured["command"] == plan.command
    assert captured["shell"] is False
