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


def test_registry_persists_and_removes_hosts(tmp_path) -> None:
    storage = tmp_path / "remote-hosts.json"
    host = RemoteHost(
        name="server",
        kind=RemoteHostKind.SSH,
        hostname="10.0.0.10",
        user="ubuntu",
        identity_file="/home/user/.ssh/id_ed25519",
        known_hosts_file="/home/user/.ssh/known_hosts",
    )

    RemoteHostRegistry(storage).register(host)
    loaded = RemoteHostRegistry(storage)

    assert loaded.get("SERVER") == host
    assert storage.stat().st_mode & 0o777 == 0o600

    assert loaded.remove("server") == host
    assert RemoteHostRegistry(storage).all() == ()


def test_registry_rejects_corrupted_inventory(tmp_path) -> None:
    storage = tmp_path / "remote-hosts.json"
    storage.write_text("not-json", encoding="utf-8")

    with pytest.raises(ValueError, match="corrompido"):
        RemoteHostRegistry(storage)
