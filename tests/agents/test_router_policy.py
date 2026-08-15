from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.agents.policy import AgentPolicy
from ubuntu_ai.agents.router import AgentRouter


def test_router_uses_task_kind() -> None:
    task = AgentTask(kind=AgentKind.PLANNER, payload="x")

    assert AgentRouter().route(task) is AgentKind.PLANNER


def test_policy_rejects_empty_execution_payload() -> None:
    decision = AgentPolicy().evaluate(AgentTask(kind=AgentKind.EXECUTION, payload=None))

    assert not decision.allowed
