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
