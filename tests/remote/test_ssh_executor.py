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
    assert runner.argv[0] == "ssh"
    assert "BatchMode=yes" in runner.argv
    assert "PasswordAuthentication=no" in runner.argv
    assert "KbdInteractiveAuthentication=no" in runner.argv
    assert "StrictHostKeyChecking=yes" in runner.argv
    assert "ConnectTimeout=10" in runner.argv
    assert runner.argv[runner.argv.index("-p") + 1] == "2222"
    assert "ubuntu@example.local" in runner.argv


def test_ssh_executor_uses_explicit_identity_and_known_hosts() -> None:
    runner = FakeRunner()

    SSHExecutor(runner).execute(
        RemoteHost(
            name="server",
            kind=RemoteHostKind.SSH,
            hostname="example.local",
            identity_file="/home/user/.ssh/id_ed25519",
            known_hosts_file="/home/user/.ssh/known_hosts",
        ),
        RemoteCommand(("printf", "%s", "hello; reboot")),
    )

    assert runner.argv[runner.argv.index("-i") + 1] == "/home/user/.ssh/id_ed25519"
    assert "IdentitiesOnly=yes" in runner.argv
    assert "UserKnownHostsFile=/home/user/.ssh/known_hosts" in runner.argv
    assert runner.argv[-1] == "printf %s 'hello; reboot'"
