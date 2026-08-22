from datetime import datetime

import pytest

from ubuntu_ai.context import SystemHealthService, SystemMetrics
from ubuntu_ai.fast_path import InstalledSoftwareResponder, LocalResponder


@pytest.fixture
def responder() -> LocalResponder:
    return LocalResponder(lambda: datetime(2026, 8, 18, 21, 7))


@pytest.mark.parametrize(
    "phrase",
    [
        "que dia é hoje?",
        "Qual a data de hoje?",
        "hoje é que dia",
        "mostre o dia e mês atuais",
        "informe o dia e o mês atual",
        "qual a data atual?",
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
    [
        "que mês estamos?",
        "qual é o mês atual?",
        "em que mes estamos?",
        "mês atual",
    ],
)
def test_current_month_is_answered_locally(
    responder: LocalResponder,
    phrase: str,
) -> None:
    response = responder.respond(phrase)

    assert response is not None
    assert response.route == "local"
    assert response.text == "Estamos em agosto de 2026."


@pytest.mark.parametrize(
    "phrase",
    [
        "que ano estamos?",
        "qual é o ano atual?",
        "mostre o ano atual",
    ],
)
def test_current_year_is_answered_locally(
    responder: LocalResponder,
    phrase: str,
) -> None:
    response = responder.respond(phrase)

    assert response is not None
    assert response.route == "local"
    assert response.text == "Estamos em 2026."


@pytest.mark.parametrize(
    "phrase",
    [
        "que horas são?",
        "hora atual",
        "HORÁRIO ATUAL",
        "mostre as horas",
        "informe o horário atual",
    ],
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
    assert "Informações do computador" in response.text
    assert "Comandos Linux" in response.text
    assert "confirmação" in response.text


def test_ubuntu_version_is_answered_locally(responder: LocalResponder) -> None:
    response = responder.respond("qual a versão do Ubuntu?")

    assert response is not None
    assert response.route == "local"
    assert "Sistema deste computador:" in response.text


def test_linux_command_help_is_answered_locally(responder: LocalResponder) -> None:
    response = responder.respond("explique o comando chmod")

    assert response is not None
    assert "chmod u+x script.sh" in response.text


def test_installed_programs_are_answered_locally() -> None:
    responder = LocalResponder(software=InstalledSoftwareResponder(lambda: (("firefox", "141.0"),)))

    response = responder.respond("quais programas tenho instalados?")

    assert response is not None
    assert "firefox" in response.text


def test_unknown_request_continues_to_planners(
    responder: LocalResponder,
) -> None:
    assert responder.respond("configure o nginx") is None


def test_system_health_is_answered_locally_without_ollama() -> None:
    sample = SystemMetrics(
        cpu_percent=12.0,
        memory_percent=45.0,
        memory_available_mb=3500,
        swap_percent=5.0,
        disk_percent=60.0,
        disk_free_gb=80.0,
        active_network_interfaces=2,
        process_count=140,
        uptime_seconds=3600,
    )
    responder = LocalResponder(
        health_service=SystemHealthService(lambda: sample),
    )

    response = responder.respond("como está este computador?")

    assert response is not None
    assert "saudável" in response.text
    assert "CPU: 12.0%" in response.text
    assert "RAM: 45.0%" in response.text
