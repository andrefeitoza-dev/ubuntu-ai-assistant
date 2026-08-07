from ubuntu_ai.remote.connection import ConnectionResolver
from ubuntu_ai.remote.models import RemoteHost, RemoteHostKind


def test_ssh_address_includes_user() -> None:
    spec = ConnectionResolver().resolve(
        RemoteHost(
            name="server",
            kind=RemoteHostKind.SSH,
            hostname="example.local",
            user="ubuntu",
        )
    )

    assert spec.address == "ubuntu@example.local"
    assert spec.is_remote
