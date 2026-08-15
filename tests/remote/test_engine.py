import pytest

from ubuntu_ai.remote.engine import (
    RemoteConfirmationRequired,
    RemoteExecutionEngine,
)
from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteExecutionResult,
    RemoteHost,
    RemoteHostKind,
)
from ubuntu_ai.remote.registry import RemoteHostRegistry


class FakeExecutor:
    def execute(self, host, command):
        return RemoteExecutionResult(
            host=host.name,
            command=command.argv,
            return_code=0,
            stdout="ok",
            stderr="",
        )


def build_engine() -> RemoteExecutionEngine:
    registry = RemoteHostRegistry()
    registry.register(
        RemoteHost(
            name="server",
            kind=RemoteHostKind.SSH,
            hostname="server.local",
        )
    )

    return RemoteExecutionEngine(
        registry,
        ssh_executor=FakeExecutor(),
    )


def test_engine_dispatches_to_executor() -> None:
    result = build_engine().execute(
        "server",
        RemoteCommand(("uname", "-a")),
    )

    assert result.success


def test_engine_requires_confirmation_for_reboot() -> None:
    with pytest.raises(RemoteConfirmationRequired):
        build_engine().execute(
            "server",
            RemoteCommand(("reboot",)),
        )
