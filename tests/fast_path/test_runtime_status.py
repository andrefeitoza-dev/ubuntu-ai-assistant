from __future__ import annotations

import pytest

from ubuntu_ai.fast_path import RuntimeStatusResponder
from ubuntu_ai.interaction import InteractionRoute, InteractionRouter


@pytest.fixture
def responder() -> RuntimeStatusResponder:
    return RuntimeStatusResponder(
        ssh_provider=lambda: "ativo",
        docker_provider=lambda: "Docker version 27.0.0",
        python_provider=lambda: "3.12.14",
        version_provider=lambda: "2.1.0",
        installation_provider=lambda: "2.1.0",
    )


@pytest.mark.parametrize(
    ("phrase", "expected"),
    (
        ("O serviço SSH está ativo?", "Serviço SSH"),
        ("O Docker está instalado?", "Docker version 27.0.0"),
        ("Qual a versão do Python?", "3.12.14"),
        ("Mostre a versão do assistente.", "2.1.0"),
        ("Verifique a instalação.", "disponível e legível"),
    ),
)
def test_runtime_queries_are_answered_locally(
    responder: RuntimeStatusResponder,
    phrase: str,
    expected: str,
) -> None:
    response = responder.respond(phrase)

    assert response is not None
    assert expected in response


def test_unknown_request_is_not_intercepted(
    responder: RuntimeStatusResponder,
) -> None:
    assert responder.respond("Explique como funciona o Docker.") is None


@pytest.mark.parametrize(
    "phrase",
    (
        "O serviço SSH está ativo?",
        "O Docker está instalado?",
        "Qual a versão do Python?",
        "Mostre a versão do assistente.",
        "Verifique a instalação.",
    ),
)
def test_runtime_catalog_examples_use_local_route(
    phrase: str,
) -> None:
    decision = InteractionRouter().route(phrase)

    assert decision.route is InteractionRoute.LOCAL
    assert decision.response
