import pytest

from ubuntu_ai.agents.models import AgentKind
from ubuntu_ai.agents.orchestration import OrchestrationStatus
from ubuntu_ai.agents.selection import (
    OrchestrationPlanner,
    SpecialistSelector,
    build_specialist_orchestrator,
)
from ubuntu_ai.agents.specialists import AgentEnvironment


@pytest.mark.parametrize(
    ("phrase", "expected"),
    (
        ("verifique CPU e memória", (AgentKind.SYSTEM,)),
        ("analise rede, DNS e gateway", (AgentKind.NETWORK,)),
        ("quanto espaço existe nos discos?", (AgentKind.STORAGE,)),
        ("existem serviços em falha?", (AgentKind.SERVICES,)),
        (
            "verifique rede e armazenamento",
            (AgentKind.NETWORK, AgentKind.STORAGE),
        ),
    ),
)
def test_selector_chooses_explicit_domains(phrase: str, expected) -> None:
    assert SpecialistSelector().select(phrase).specialists == expected


def test_complete_diagnostic_selects_all_specialists_in_stable_order() -> None:
    selection = SpecialistSelector().select("Faça um diagnóstico completo")

    assert selection.specialists == (
        AgentKind.SYSTEM,
        AgentKind.NETWORK,
        AgentKind.STORAGE,
        AgentKind.SERVICES,
    )


def test_selector_refuses_request_without_supported_domain() -> None:
    with pytest.raises(ValueError, match="Nenhum especialista"):
        SpecialistSelector().select("escreva uma história sobre tecnologia")


def test_planner_builds_bounded_read_only_goal() -> None:
    goal = OrchestrationPlanner().plan(
        "verifique rede e serviços",
        goal_id="health-check",
    )

    assert [task.specialist for task in goal.tasks] == [
        AgentKind.NETWORK,
        AgentKind.SERVICES,
    ]
    assert all(len(task.payload.actions) == 1 for task in goal.tasks)
    assert all(not task.payload.confirmed for task in goal.tasks)
    assert dict(goal.context)["target"] == "local"


def test_remote_planner_requires_explicit_target() -> None:
    with pytest.raises(ValueError, match="destino explícito"):
        OrchestrationPlanner().plan(
            "verifique a rede",
            goal_id="remote",
            environment=AgentEnvironment.REMOTE,
        )


def test_planned_goal_coordinates_all_specialists() -> None:
    goal = OrchestrationPlanner().plan(
        "diagnóstico completo",
        goal_id="complete",
    )

    result = build_specialist_orchestrator().run(goal)

    assert result.status is OrchestrationStatus.COMPLETED
    assert result.progress == 1.0
    assert [item.specialist for item in result.tasks] == [
        AgentKind.SYSTEM,
        AgentKind.NETWORK,
        AgentKind.STORAGE,
        AgentKind.SERVICES,
    ]
