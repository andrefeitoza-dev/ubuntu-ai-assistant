from ubuntu_ai.remote.context import RemoteContextBuilder
from ubuntu_ai.remote.models import RemoteHost, RemoteHostKind


def test_remote_context_is_host_scoped() -> None:
    context = RemoteContextBuilder().build(
        RemoteHost(
            name="server",
            kind=RemoteHostKind.SSH,
            hostname="server.local",
            user="ubuntu",
        )
    )

    assert context.host_name == "server"
    assert context.kind == "ssh"
