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


class FactEngine:
    OUTPUTS = {
        ("cat", "/etc/os-release"): 'PRETTY_NAME="Ubuntu 24.04 LTS"\n',
        ("free", "-m"): (
            "               total used free shared buff/cache available\n"
            "Mem:            8192 2048 4096 100 2048 6144\n"
        ),
        ("df", "-h", "/"): (
            "Filesystem Size Used Avail Use% Mounted on\n/dev/sda2 100G 40G 60G 40% /\n"
        ),
    }

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[str, ...]]] = []

    def execute(self, host_name, command):
        self.calls.append((host_name, command.argv))
        output = self.OUTPUTS.get(command.argv, "ok\n")
        return RemoteExecutionResult(host_name, command.argv, 0, output, "")


def test_remote_fact_uses_only_requested_read_only_command() -> None:
    engine = FactEngine()
    service = RemoteDiagnosticService(engine)  # type: ignore[arg-type]

    response = service.answer_fact("production", "operating_system")

    assert response == "Computador remoto: production\nSistema: Ubuntu 24.04 LTS"
    assert engine.calls == [("production", ("cat", "/etc/os-release"))]


def test_remote_memory_and_disk_are_presented_without_shell_wrappers() -> None:
    engine = FactEngine()
    service = RemoteDiagnosticService(engine)  # type: ignore[arg-type]

    memory = service.answer_fact("production", "memory")
    disk = service.answer_fact("production", "disk")

    assert "8192 MiB no total · 6144 MiB disponíveis" in memory
    assert "40% usado · 60G disponíveis" in disk
    assert all(command[0] not in {"bash", "sh", "sudo"} for _, command in engine.calls)
