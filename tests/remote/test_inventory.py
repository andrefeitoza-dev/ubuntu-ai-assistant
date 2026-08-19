import pytest

from ubuntu_ai.remote.inventory import RemoteInventoryService
from ubuntu_ai.remote.registry import RemoteHostRegistry


def test_inventory_registers_updates_lists_and_removes_ssh_host(tmp_path) -> None:
    service = RemoteInventoryService(RemoteHostRegistry(tmp_path / "hosts.json"))

    created = service.register_ssh(
        name="production",
        hostname="10.0.0.20",
        user="ubuntu",
        identity_file="/home/user/.ssh/id_ed25519",
        known_hosts_file="/home/user/.ssh/known_hosts",
    )
    updated = service.update_ssh("production", port=2222)

    assert created.port == 22
    assert updated.port == 2222
    assert service.list_hosts() == (updated,)
    assert service.remove("production") == updated
    assert service.list_hosts() == ()


def test_inventory_rejects_unknown_update_field() -> None:
    service = RemoteInventoryService(RemoteHostRegistry())
    service.register_ssh(name="server", hostname="server.local")

    with pytest.raises(ValueError, match="não permitidos"):
        service.update_ssh("server", password="secret")
