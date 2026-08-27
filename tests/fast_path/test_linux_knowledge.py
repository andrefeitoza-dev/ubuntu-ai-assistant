from __future__ import annotations

from ubuntu_ai.fast_path import LinuxKnowledgeResponder
from ubuntu_ai.interaction import InteractionRoute, InteractionRouter


def test_systemd_explanation_is_local_and_precise() -> None:
    response = LinuxKnowledgeResponder().respond("Explique como funciona o systemd.")

    assert response is not None
    assert "PID 1" in response
    assert "systemctl" in response
    assert "journalctl" in response


def test_service_explanation_is_local_and_precise() -> None:
    response = LinuxKnowledgeResponder().respond("O que é um serviço?")

    assert response is not None
    assert "segundo plano" in response
    assert ".service" in response
    assert "systemd" in response


def test_unrelated_knowledge_continues_to_chat() -> None:
    assert LinuxKnowledgeResponder().respond("Explique o funcionamento do Kubernetes.") is None


def test_announced_linux_knowledge_examples_use_local_route() -> None:
    router = InteractionRouter()

    for phrase in (
        "Explique como funciona o systemd.",
        "O que é um serviço?",
    ):
        decision = router.route(phrase)
        assert decision.route is InteractionRoute.LOCAL
        assert decision.response
