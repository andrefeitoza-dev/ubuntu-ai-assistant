from ubuntu_ai.remote.diagnostics import RemoteDiagnosticService
from ubuntu_ai.remote.models import RemoteExecutionResult


class FakeEngine:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def execute(self, host_name, command):
        self.calls.append((host_name, command.argv))
        return RemoteExecutionResult(host_name, command.argv, 0, "ok", "")


def test_diagnostics_collects_host_scoped_read_only_context() -> None:
    engine = FakeEngine()

    context = RemoteDiagnosticService(engine).collect("production")  # type: ignore[arg-type]

    assert context.host_name == "production"
    assert context.get("system").output == "ok"
    assert {item.name for item in context.items} == {
        "system",
        "cpu",
        "memory",
        "disk",
        "network",
        "services",
    }
    assert all(host == "production" for host, _command in engine.calls)
