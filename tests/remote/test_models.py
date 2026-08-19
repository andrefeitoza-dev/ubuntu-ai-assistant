import pytest

from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteHost,
    RemoteHostKind,
)


def test_ssh_host_requires_hostname() -> None:
    with pytest.raises(ValueError):
        RemoteHost(
            name="server",
            kind=RemoteHostKind.SSH,
        )


def test_command_requires_argv() -> None:
    with pytest.raises(ValueError):
        RemoteCommand(())


@pytest.mark.parametrize(
    "hostname",
    ("server;reboot", "server name", "../server", "server$(id)"),
)
def test_ssh_host_rejects_unsafe_hostname(hostname: str) -> None:
    with pytest.raises(ValueError):
        RemoteHost(name="server", kind=RemoteHostKind.SSH, hostname=hostname)


def test_ssh_host_rejects_unsafe_user() -> None:
    with pytest.raises(ValueError):
        RemoteHost(
            name="server",
            kind=RemoteHostKind.SSH,
            hostname="server.local",
            user="ubuntu;id",
        )


def test_ssh_files_require_absolute_paths() -> None:
    with pytest.raises(ValueError, match="caminho absoluto"):
        RemoteHost(
            name="server",
            kind=RemoteHostKind.SSH,
            hostname="server.local",
            identity_file="id_ed25519",
        )


def test_command_rejects_nul_and_unbounded_timeout() -> None:
    with pytest.raises(ValueError):
        RemoteCommand(("echo", "bad\0argument"))
    with pytest.raises(ValueError):
        RemoteCommand(("echo",), timeout=301)
