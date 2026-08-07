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
