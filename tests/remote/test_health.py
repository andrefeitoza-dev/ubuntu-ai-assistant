from ubuntu_ai.remote.cancellation import RemoteExecutionCancelled
from ubuntu_ai.remote.health import RemoteHealthService


def test_health_explains_timeout() -> None:
    message = RemoteHealthService._friendly_error(
        TimeoutError("connection timed out"),
    )

    assert "tempo configurado" in message


def test_health_explains_unknown_server_identity() -> None:
    message = RemoteHealthService._friendly_error(
        RuntimeError("Host key verification failed"),
    )

    assert "identidade SSH" in message


def test_health_explains_refused_ssh_key() -> None:
    message = RemoteHealthService._friendly_error(
        RuntimeError("Permission denied (publickey)"),
    )

    assert "chave SSH" in message


def test_health_explains_cancellation() -> None:
    message = RemoteHealthService._friendly_error(
        RemoteExecutionCancelled("cancelled"),
    )

    assert "cancelado pelo usuário" in message
