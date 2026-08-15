import pytest

from ubuntu_ai.remote.models import RemoteHost, RemoteHostKind
from ubuntu_ai.remote.registry import RemoteHostRegistry


def test_registry_registers_host() -> None:
    registry = RemoteHostRegistry()
    host = RemoteHost(
        name="server",
        kind=RemoteHostKind.SSH,
        hostname="10.0.0.10",
    )

    registry.register(host)

    assert registry.get("server") is host


def test_registry_rejects_duplicate() -> None:
    registry = RemoteHostRegistry()
    host = RemoteHost(
        name="local",
        kind=RemoteHostKind.LOCAL,
    )

    registry.register(host)

    with pytest.raises(ValueError):
        registry.register(host)
