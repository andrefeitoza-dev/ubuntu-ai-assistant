from types import SimpleNamespace

import pytest

from ubuntu_ai.context import HealthStatus, SystemHealthSnapshot, SystemMetrics
from ubuntu_ai.fast_path import SystemFactResponder


class Detector:
    def __init__(self, value):
        self.value = value

    def detect(self):
        return self.value


@pytest.fixture
def responder() -> SystemFactResponder:
    health = SystemHealthSnapshot(
        SystemMetrics(12, 50, 4096, 0, 60, 80, 2, 140, 3600),
        HealthStatus.HEALTHY,
    )
    return SystemFactResponder(
        operating_system=Detector("Ubuntu 24.04.3 LTS"),  # type: ignore[arg-type]
        kernel=Detector("6.8.0-test"),  # type: ignore[arg-type]
        hostname=Detector("notebook"),  # type: ignore[arg-type]
        cpu=Detector("Intel CPU"),  # type: ignore[arg-type]
        memory=Detector(8192),  # type: ignore[arg-type]
        health=SimpleNamespace(snapshot=lambda: health),
        battery_provider=lambda: 78.0,
        failed_services_provider=lambda: 0,
    )


@pytest.mark.parametrize(
    "phrase",
    (
        "qual a versão do Ubuntu?",
        "qual é o kernel deste computador?",
        "quanto tenho de memória?",
        "quanto espaço livre tenho no disco?",
        "quantos processos estão em execução?",
        "mostre o estado da rede",
        "qual o nível da bateria?",
        "existem serviços em falha?",
        "mostre um resumo deste computador",
    ),
)
def test_factual_requests_are_detected(phrase: str) -> None:
    assert SystemFactResponder.matches(phrase)


def test_ubuntu_version_uses_real_system_fact(responder: SystemFactResponder) -> None:
    assert responder.respond("qual a versao do ubuntu") == (
        "Sistema deste computador: Ubuntu 24.04.3 LTS."
    )


def test_memory_reports_total_and_available(responder: SystemFactResponder) -> None:
    response = responder.respond("quanto tenho de memoria")

    assert response is not None
    assert "8.0 GiB no total" in response
    assert "4.0 GiB disponíveis" in response


def test_summary_identifies_local_target(responder: SystemFactResponder) -> None:
    response = responder.respond("mostre um resumo deste computador")

    assert response is not None
    assert "Computador: local" in response
    assert "Ubuntu 24.04.3 LTS" in response
    assert "notebook" in response
    assert "Bateria: 78%" in response
    assert "Serviços em falha: 0" in response


def test_battery_and_services_use_read_only_providers(
    responder: SystemFactResponder,
) -> None:
    assert responder.respond("qual o nivel da bateria") == ("Bateria deste computador: 78%.")
    assert responder.respond("existem servicos em falha") == (
        "Não existem serviços do sistema em estado de falha."
    )


def test_conceptual_question_is_not_treated_as_machine_fact() -> None:
    assert not SystemFactResponder.matches("o que é memória RAM?")
