from pathlib import Path

import pytest

from ubuntu_ai.desktop import DesktopApplicationCatalog
from ubuntu_ai.execution import ExecutionRequest
from ubuntu_ai.execution.default_policy import DefaultExecutionPolicy


def test_policy_allows_safe_command() -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(ExecutionRequest(command="ls -la"))

    assert decision.allowed is True
    assert decision.reason == "Comando autorizado."


def test_policy_blocks_rm() -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(ExecutionRequest(command="rm -rf /"))

    assert decision.allowed is False
    assert "bloqueado" in decision.reason


def test_policy_blocks_empty_command() -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(ExecutionRequest(command=""))

    assert decision.allowed is False
    assert decision.reason == "Comando vazio."


def test_policy_blocks_shutdown() -> None:
    policy = DefaultExecutionPolicy()

    decision = policy.evaluate(ExecutionRequest(command="shutdown now"))

    assert decision.allowed is False


def test_policy_allows_trusted_desktop_application() -> None:
    decision = DefaultExecutionPolicy().evaluate(ExecutionRequest(command="gtk-launch firefox"))

    assert decision.allowed is True


def test_policy_blocks_unknown_desktop_application() -> None:
    decision = DefaultExecutionPolicy().evaluate(
        ExecutionRequest(command="gtk-launch unknown.desktop")
    )

    assert decision.allowed is False
    assert "Aplicativo bloqueado" in decision.reason


def test_policy_allows_http_site() -> None:
    decision = DefaultExecutionPolicy().evaluate(
        ExecutionRequest(command="xdg-open https://ubuntu.com")
    )

    assert decision.allowed is True


def test_policy_blocks_unsafe_uri_scheme() -> None:
    decision = DefaultExecutionPolicy().evaluate(
        ExecutionRequest(command="xdg-open javascript:alert(1)")
    )

    assert decision.allowed is False
    assert "Destino bloqueado" in decision.reason


@pytest.mark.parametrize(
    "command",
    (
        "gtk-launch org.gnome.Calculator",
        "gtk-launch org.gnome.Terminal",
        "gtk-launch libreoffice-startcenter",
        "firefox https://github.com",
    ),
)
def test_policy_allows_v22_trusted_desktop_commands(
    command: str,
) -> None:
    decision = DefaultExecutionPolicy().evaluate(ExecutionRequest(command=command))

    assert decision.allowed is True


@pytest.mark.parametrize(
    "command",
    (
        "gnome-terminal -- bash -c id",
        "gnome-calculator --help",
        "libreoffice --headless",
        "gtk-launch libreoffice-startcenter --headless",
        "firefox file:///etc/passwd",
        "firefox javascript:alert(1)",
        "firefox data:text/html,unsafe",
        "firefox https://user:password@example.com",
        "firefox https://example.com:invalid",
        "firefox 'https://example.com\nunsafe'",
        "firefox --new-window https://example.com",
    ),
)
def test_policy_blocks_arguments_outside_v22_contract(
    command: str,
) -> None:
    decision = DefaultExecutionPolicy().evaluate(ExecutionRequest(command=command))

    assert decision.allowed is False


def test_policy_independently_allows_discovered_system_entry(tmp_path) -> None:
    entry = tmp_path / "org.gimp.GIMP.desktop"
    entry.write_text(
        "[Desktop Entry]\nType=Application\nName=GIMP\nExec=gimp %U\n",
        encoding="utf-8",
    )
    entry.chmod(0o644)
    policy = DefaultExecutionPolicy(DesktopApplicationCatalog((tmp_path,)))

    decision = policy.evaluate(ExecutionRequest(command="gtk-launch org.gimp.GIMP"))

    assert decision.allowed is True


def test_policy_allows_non_overwriting_change_inside_home(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: tmp_path))
    source = tmp_path / "origem.txt"
    source.write_text("dados", encoding="utf-8")
    destination = tmp_path / "destino.txt"

    decision = DefaultExecutionPolicy().evaluate(
        ExecutionRequest(command=f"cp {source} {destination}")
    )

    assert decision.allowed is True


@pytest.mark.parametrize("executable", ("mkdir", "cp", "mv"))
def test_policy_blocks_file_change_outside_home(tmp_path, monkeypatch, executable) -> None:
    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: tmp_path))
    command = (
        f"{executable} /tmp/fora"
        if executable == "mkdir"
        else f"{executable} {tmp_path / 'origem'} /tmp/fora"
    )

    decision = DefaultExecutionPolicy().evaluate(ExecutionRequest(command=command))

    assert decision.allowed is False


def test_policy_allows_only_existing_non_symlink_item_to_trash(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(Path, "home", classmethod(lambda _cls: tmp_path))
    source = tmp_path / "rascunho.txt"
    source.write_text("dados", encoding="utf-8")

    allowed = DefaultExecutionPolicy().evaluate(ExecutionRequest(command=f"gio trash {source}"))
    blocked = DefaultExecutionPolicy().evaluate(ExecutionRequest(command="gio trash /etc/passwd"))

    assert allowed.allowed is True
    assert blocked.allowed is False


@pytest.mark.parametrize(
    "command",
    (
        "pkexec apt-get update",
        "pkexec apt-get upgrade -y",
        "pkexec apt-get autoremove -y",
        "pkexec apt-get clean",
        "pkexec ufw enable",
    ),
)
def test_policy_allows_only_declared_privileged_maintenance(command: str) -> None:
    assert DefaultExecutionPolicy().evaluate(ExecutionRequest(command=command)).allowed is True


@pytest.mark.parametrize(
    "command",
    (
        "pkexec bash",
        "pkexec apt-get dist-upgrade -y",
        "pkexec apt-get install unknown -y",
        "pkexec ufw disable",
        "pkexec rm -rf /",
    ),
)
def test_policy_blocks_other_privileged_commands(command: str) -> None:
    decision = DefaultExecutionPolicy().evaluate(ExecutionRequest(command=command))

    assert decision.allowed is False
    assert "fora da lista segura" in decision.reason
