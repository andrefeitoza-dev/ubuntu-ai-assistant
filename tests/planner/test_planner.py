import pytest

from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.planner.planner import Planner


def test_create_docker_plan() -> None:
    planner = Planner()

    plan = planner.create_plan("Instale Docker")

    assert plan.goal == "Instalar e configurar o Docker"
    assert plan.risk == RiskLevel.HIGH
    assert plan.estimated_seconds == 240
    assert len(plan.steps) == 4

    assert plan.steps[0].command == ["sudo", "apt", "update"]
    assert plan.steps[-1].command == ["docker", "--version"]


def test_reject_empty_request() -> None:
    planner = Planner()

    with pytest.raises(
        ValueError,
        match="A solicitação não pode estar vazia",
    ):
        planner.create_plan("   ")


def test_reject_unsupported_request() -> None:
    planner = Planner()

    with pytest.raises(
        ValueError,
        match="Ainda não sei criar um plano",
    ):
        planner.create_plan("Configure o servidor de e-mail")
