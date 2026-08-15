from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteHost,
    RemoteHostKind,
)
from ubuntu_ai.remote.runner import ProcessResult
from ubuntu_ai.remote.ssh_executor import SSHExecutor


class FakeRunner:
    def __init__(self) -> None:
        self.argv = None

    def run(self, argv, *, timeout):
        self.argv = tuple(argv)
        return ProcessResult(0, "ok", "")


def test_ssh_executor_builds_safe_argv() -> None:
    runner = FakeRunner()
    executor = SSHExecutor(runner)

    result = executor.execute(
        RemoteHost(
            name="server",
            kind=RemoteHostKind.SSH,
            hostname="example.local",
            user="ubuntu",
            port=2222,
        ),
        RemoteCommand(("echo", "hello world")),
    )

    assert result.success
    assert runner.argv[:4] == (
        "ssh",
        "-p",
        "2222",
        "--",
    )
    assert "ubuntu@example.local" in runner.argv
