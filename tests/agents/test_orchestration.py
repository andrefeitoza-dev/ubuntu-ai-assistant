import pytest

from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.agents.models import AgentKind
from ubuntu_ai.agents.orchestration import (
    MultiAgentOrchestrator,
    OrchestrationGoal,
    OrchestrationStatus,
    OrchestrationTask,
)
from ubuntu_ai.agents.registry import AgentRegistry
from ubuntu_ai.agents.specialists import (
    NetworkAgent,
    SpecialistAction,
    SpecialistPayload,
    StorageAgent,
    SystemAgent,
)
from ubuntu_ai.domain.risk import RiskLevel


def orchestrator() -> MultiAgentOrchestrator:
    registry = AgentRegistry()
    registry.register(SystemAgent())
    registry.register(NetworkAgent())
    registry.register(StorageAgent())
    return MultiAgentOrchestrator(AgentCoordinator(registry))


def task(
    task_id: str,
    specialist: AgentKind,
    command: tuple[str, ...],
    *,
    dependencies: tuple[str, ...] = (),
    context_keys: frozenset[str] = frozenset(),
    risk: RiskLevel = RiskLevel.LOW,
    confirmed: bool = False,
) -> OrchestrationTask:
    return OrchestrationTask(
        task_id=task_id,
        specialist=specialist,
        payload=SpecialistPayload(
            request=task_id,
            actions=(SpecialistAction(command, risk),),
            confirmed=confirmed,
        ),
        dependencies=dependencies,
        context_keys=context_keys,
    )


def test_orchestrator_orders_dependencies_and_tracks_progress() -> None:
    goal = OrchestrationGoal(
        goal_id="diagnostic",
        description="Diagnosticar computador",
        tasks=(
            task("network", AgentKind.NETWORK, ("ip", "route"), dependencies=("system",)),
            task("system", AgentKind.SYSTEM, ("uptime",)),
        ),
    )

    result = orchestrator().run(goal)

    assert result.status is OrchestrationStatus.COMPLETED
    assert [item.task_id for item in result.tasks] == ["system", "network"]
    assert result.progress == 1.0
    assert result.tasks[0].result.output.specialist is AgentKind.SYSTEM


def test_orchestrator_shares_only_requested_context() -> None:
    goal = OrchestrationGoal(
        goal_id="network",
        description="Consultar rede",
        context={"target": "local", "session_secret": "never-share"},
        tasks=(
            task(
                "route",
                AgentKind.NETWORK,
                ("ip", "route"),
                context_keys=frozenset({"target"}),
            ),
        ),
    )

    result = orchestrator().run(goal)

    assert dict(result.tasks[0].shared_context) == {"target": "local"}
    assert "session_secret" not in result.tasks[0].shared_context


@pytest.mark.parametrize(
    "tasks, message",
    (
        (
            (
                task("same", AgentKind.SYSTEM, ("uptime",)),
                task("same", AgentKind.SYSTEM, ("uptime",)),
            ),
            "duplicados",
        ),
        (
            (task("one", AgentKind.SYSTEM, ("uptime",), dependencies=("missing",)),),
            "inexistente",
        ),
        (
            (
                task("one", AgentKind.SYSTEM, ("uptime",), dependencies=("two",)),
                task("two", AgentKind.SYSTEM, ("uptime",), dependencies=("one",)),
            ),
            "ciclo",
        ),
    ),
)
def test_goal_rejects_invalid_dependency_graph(tasks, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        OrchestrationGoal("goal", "description", tasks)


def test_goal_rejects_context_outside_declared_scope() -> None:
    with pytest.raises(ValueError, match="Contexto inexistente"):
        OrchestrationGoal(
            "goal",
            "description",
            (
                task(
                    "system",
                    AgentKind.SYSTEM,
                    ("uptime",),
                    context_keys=frozenset({"secret"}),
                ),
            ),
        )


def test_orchestrator_keeps_confirmation_and_risk_centralized() -> None:
    goal = OrchestrationGoal(
        "sensitive",
        "Sensitive task",
        (
            task(
                "storage",
                AgentKind.STORAGE,
                ("df", "-h"),
                risk=RiskLevel.HIGH,
            ),
        ),
    )

    result = orchestrator().run(goal)

    assert result.status is OrchestrationStatus.BLOCKED
    assert result.tasks[0].status is OrchestrationStatus.FAILED
    assert "confirmação" in result.tasks[0].reason


def test_blocked_goal_reports_partial_progress() -> None:
    goal = OrchestrationGoal(
        "partial",
        "Partial goal",
        (
            task("system", AgentKind.SYSTEM, ("uptime",)),
            task(
                "storage",
                AgentKind.STORAGE,
                ("df", "-h"),
                dependencies=("system",),
                risk=RiskLevel.HIGH,
            ),
            task(
                "network",
                AgentKind.NETWORK,
                ("ip", "route"),
                dependencies=("storage",),
            ),
        ),
    )

    result = orchestrator().run(goal)

    assert result.status is OrchestrationStatus.BLOCKED
    assert result.progress == pytest.approx(2 / 3)


def test_orchestration_task_rejects_non_specialist_agent() -> None:
    with pytest.raises(ValueError, match="especializado"):
        task("planner", AgentKind.PLANNER, ("uptime",))
