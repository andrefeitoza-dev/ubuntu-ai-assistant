from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.agents.policy import AgentPolicy
from ubuntu_ai.agents.router import AgentRouter


def test_router_uses_task_kind() -> None:
    task = AgentTask(kind=AgentKind.PLANNER, payload="x")

    assert AgentRouter().route(task) is AgentKind.PLANNER


def test_policy_rejects_empty_execution_payload() -> None:
    decision = AgentPolicy().evaluate(AgentTask(kind=AgentKind.EXECUTION, payload=None))

    assert not decision.allowed


def test_policy_blocks_unconfirmed_sensitive_task() -> None:
    decision = AgentPolicy().evaluate(
        AgentTask(
            kind=AgentKind.SERVICES,
            payload="plan",
            metadata={"risk": "high"},
        )
    )

    assert not decision.allowed
    assert "confirmação" in decision.reason


def test_policy_blocks_critical_even_when_confirmed() -> None:
    decision = AgentPolicy().evaluate(
        AgentTask(
            kind=AgentKind.STORAGE,
            payload="plan",
            metadata={"risk": "critical", "confirmed": True},
        )
    )

    assert not decision.allowed


def test_policy_requires_remote_target() -> None:
    decision = AgentPolicy().evaluate(
        AgentTask(
            kind=AgentKind.SYSTEM,
            payload="plan",
            metadata={"environment": "remote"},
        )
    )

    assert not decision.allowed
    assert "destino" in decision.reason
