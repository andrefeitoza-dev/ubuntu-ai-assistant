from types import SimpleNamespace

import pytest

from ubuntu_ai.gui import backend as gui_backend
from ubuntu_ai.remote.engine import RemoteExecutionEngine
from ubuntu_ai.remote.models import RemoteHost, RemoteHostKind
from ubuntu_ai.remote.registry import RemoteHostRegistry


@pytest.fixture
def backend(monkeypatch):
    registry = RemoteHostRegistry()
    registry.register(RemoteHost(name="local", kind=RemoteHostKind.LOCAL))
    runtime = SimpleNamespace(remote=RemoteExecutionEngine(registry))
    monkeypatch.setattr(gui_backend.container, "application_runtime", lambda: runtime)
    monkeypatch.setattr(gui_backend.container, "interaction_router", lambda: object())
    monkeypatch.setattr(gui_backend.container, "chat_service", lambda: object())
    return gui_backend.GUIBackend()


def test_backend_requires_explicit_remote_target(backend) -> None:
    with pytest.raises(ValueError, match="Selecione explicitamente"):
        backend.remote_diagnostics()


def test_backend_registers_selects_and_removes_remote_host(backend) -> None:
    host = backend.register_remote_host(
        name="production",
        hostname="server.local",
        user="ubuntu",
        port=22,
        identity_file=None,
        known_hosts_file=None,
    )

    assert backend.remote_hosts() == (host,)
    assert backend.select_target("production") == host
    assert backend.is_remote_selected

    backend.remove_remote_host("production")

    assert backend.selected_target == "local"
    assert not backend.is_remote_selected


def test_backend_never_removes_local_target(backend) -> None:
    with pytest.raises(ValueError, match="não pode ser removido"):
        backend.remove_remote_host("local")


def test_backend_never_answers_remote_fact_with_local_data(backend) -> None:
    backend.register_remote_host(
        name="production",
        hostname="server.local",
        user="ubuntu",
        port=22,
        identity_file=None,
        known_hosts_file=None,
    )
    backend.select_target("production")

    decision = backend.route("qual a versão do Ubuntu?")

    assert "production" in decision.response
    assert "nenhuma informação do computador local" in decision.response


def test_backend_exposes_twenty_capability_topics(backend) -> None:
    topics = backend.capability_topics()

    assert len(topics) == 20
    assert topics[0].title == "Informações do computador"
    assert "Risco:" in backend.capability_detail("04")
