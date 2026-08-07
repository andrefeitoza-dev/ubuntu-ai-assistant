from ubuntu_ai.remote.local_executor import LocalExecutor
from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteHost,
    RemoteHostKind,
)
from ubuntu_ai.remote.runner import ProcessResult


class FakeRunner:
    def run(self, argv, *, timeout):
        return ProcessResult(0, "local-ok", "")


def test_local_executor_normalizes_result() -> None:
    result = LocalExecutor(FakeRunner()).execute(
        RemoteHost(
            name="local",
            kind=RemoteHostKind.LOCAL,
        ),
        RemoteCommand(("echo", "ok")),
    )

    assert result.success
    assert result.stdout == "local-ok"
