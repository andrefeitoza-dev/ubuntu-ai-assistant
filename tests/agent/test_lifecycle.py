from ubuntu_ai.agent.lifecycle import AgentLifecycle


def test_agent_lifecycle_contains_expected_states() -> None:
    assert AgentLifecycle.IDLE.value == "idle"
    assert AgentLifecycle.PLANNING.value == "planning"
    assert (
        AgentLifecycle.WAITING_CONFIRMATION.value
        == "waiting_confirmation"
    )
    assert AgentLifecycle.EXECUTING.value == "executing"
    assert AgentLifecycle.COMPLETED.value == "completed"
    assert AgentLifecycle.FAILED.value == "failed"