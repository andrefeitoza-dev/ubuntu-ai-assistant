from datetime import datetime

import pytest

from ubuntu_ai.fast_path import LocalResponder


@pytest.fixture
def responder() -> LocalResponder:
    return LocalResponder(lambda: datetime(2026, 8, 18, 21, 7))


@pytest.mark.parametrize(
    "phrase",
    [
        "que dia é hoje?",
        "Qual a data de hoje?",
        "hoje é que dia",
    ],
)
def test_date_is_answered_locally(
    responder: LocalResponder,
    phrase: str,
) -> None:
    response = responder.respond(phrase)

    assert response is not None
    assert response.route == "local"
    assert response.text == "Hoje é terça-feira, 18 de agosto de 2026."


@pytest.mark.parametrize(
    "phrase",
    ["que horas são?", "hora atual", "HORÁRIO ATUAL"],
)
def test_time_is_answered_locally(
    responder: LocalResponder,
    phrase: str,
) -> None:
    response = responder.respond(phrase)

    assert response is not None
    assert response.text == "Agora são 21:07."


def test_help_is_answered_locally(responder: LocalResponder) -> None:
    response = responder.respond("help")

    assert response is not None
    assert "arquivos" in response.text
    assert "confirmação" in response.text


def test_unknown_request_continues_to_planners(
    responder: LocalResponder,
) -> None:
    assert responder.respond("configure o nginx") is None
