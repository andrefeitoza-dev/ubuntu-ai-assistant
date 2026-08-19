from ubuntu_ai.remote.docker_executor import DockerExecutor
from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteHost,
    RemoteHostKind,
)
from ubuntu_ai.remote.runner import ProcessResult


class FakeRunner:
    def __init__(self) -> None:
        self.argv = None

    def run(self, argv, *, timeout, cancellation=None):
        self.argv = tuple(argv)
        return ProcessResult(0, "docker-ok", "")


def test_docker_executor_uses_docker_exec() -> None:
    runner = FakeRunner()

    result = DockerExecutor(runner).execute(
        RemoteHost(
            name="app",
            kind=RemoteHostKind.DOCKER,
            container="ubuntu-ai-app",
        ),
        RemoteCommand(("python", "--version")),
    )

    assert result.success
    assert runner.argv[:3] == (
        "docker",
        "exec",
        "ubuntu-ai-app",
    )
