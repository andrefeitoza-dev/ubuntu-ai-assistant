from ubuntu_ai.remote.factory import build_remote_engine
from ubuntu_ai.remote.models import RemoteCommand


def test_factory_registers_local_host() -> None:
    engine = build_remote_engine()

    result = engine.execute(
        "local",
        RemoteCommand(("python", "-c", "print('ok')")),
    )

    assert result.success
    assert "ok" in result.stdout
