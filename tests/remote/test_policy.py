import pytest

from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteHost,
    RemoteHostKind,
)
from ubuntu_ai.remote.policy import RemoteExecutionPolicy


def test_destructive_command_requires_confirmation() -> None:
    decision = RemoteExecutionPolicy().evaluate(
        RemoteHost(
            name="server",
            kind=RemoteHostKind.SSH,
            hostname="server.local",
        ),
        RemoteCommand(("reboot",)),
    )

    assert decision.allowed
    assert decision.requires_confirmation


@pytest.mark.parametrize("command", (("sudo", "id"), ("su", "-c", "id"), ("bash", "-lc", "id")))
def test_policy_blocks_elevation_and_shell_wrappers(command: tuple[str, ...]) -> None:
    decision = RemoteExecutionPolicy().evaluate(
        RemoteHost(
            name="server",
            kind=RemoteHostKind.SSH,
            hostname="server.local",
        ),
        RemoteCommand(command),
    )

    assert not decision.allowed
    assert not decision.requires_confirmation
