import pytest

from ubuntu_ai.agents.models import AgentKind, AgentTask
from ubuntu_ai.agents.specialists import (
    AgentEnvironment,
    NetworkAgent,
    ServicesAgent,
    SpecialistAction,
    SpecialistPayload,
    StorageAgent,
    SystemAgent,
)
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.reflection.failure import FailureKind


@pytest.mark.parametrize(
    ("agent", "command", "kind"),
    (
        (SystemAgent(), ("free", "-h"), AgentKind.SYSTEM),
        (NetworkAgent(), ("ip", "route"), AgentKind.NETWORK),
        (StorageAgent(), ("df", "-h"), AgentKind.STORAGE),
        (ServicesAgent(), ("systemctl", "status", "ssh"), AgentKind.SERVICES),
    ),
)
def test_specialists_accept_own_read_only_actions(agent, command, kind) -> None:
    result = agent.handle(
        AgentTask(
            kind=kind,
            payload=SpecialistPayload(
                request="diagnosticar",
                actions=(SpecialistAction(command),),
            ),
        )
    )

    assert result.output.specialist is kind
    assert result.output.actions[0].risk is RiskLevel.LOW


def test_specialist_rejects_action_outside_scope() -> None:
    with pytest.raises(PermissionError, match="não permite"):
        NetworkAgent().handle(
            AgentTask(
                AgentKind.NETWORK,
                SpecialistPayload("rede", (SpecialistAction(("systemctl", "restart", "ssh")),)),
            )
        )


def test_sensitive_action_requires_confirmation() -> None:
    task = AgentTask(
        AgentKind.SERVICES,
        SpecialistPayload(
            "reiniciar ssh",
            (SpecialistAction(("systemctl", "restart", "ssh"), RiskLevel.HIGH),),
        ),
    )

    with pytest.raises(PermissionError, match="confirmação"):
        ServicesAgent().handle(task)


def test_confirmed_sensitive_action_is_only_planned() -> None:
    result = ServicesAgent().handle(
        AgentTask(
            AgentKind.SERVICES,
            SpecialistPayload(
                "reiniciar ssh",
                (SpecialistAction(("systemctl", "restart", "ssh"), RiskLevel.HIGH),),
                confirmed=True,
            ),
        )
    )

    assert result.output.actions[0].risk is RiskLevel.HIGH


def test_critical_action_is_always_blocked() -> None:
    with pytest.raises(PermissionError, match="CRITICAL"):
        StorageAgent().handle(
            AgentTask(
                AgentKind.STORAGE,
                SpecialistPayload(
                    "formatar",
                    (SpecialistAction(("df", "-h"), RiskLevel.CRITICAL),),
                    confirmed=True,
                ),
            )
        )


def test_remote_specialist_requires_explicit_target() -> None:
    with pytest.raises(PermissionError, match="destino"):
        SystemAgent().handle(
            AgentTask(
                AgentKind.SYSTEM,
                SpecialistPayload(
                    "status remoto",
                    (SpecialistAction(("uptime",)),),
                    environment=AgentEnvironment.REMOTE,
                ),
            )
        )


def test_specialist_enforces_attempt_and_duration_limits() -> None:
    with pytest.raises(PermissionError, match="tentativas"):
        SystemAgent().handle(
            AgentTask(
                AgentKind.SYSTEM,
                SpecialistPayload("status", (SpecialistAction(("uptime",)),), attempt=4),
            )
        )

    with pytest.raises(PermissionError, match="duração"):
        SystemAgent().handle(
            AgentTask(
                AgentKind.SYSTEM,
                SpecialistPayload(
                    "status",
                    (SpecialistAction(("uptime",)),),
                    elapsed_seconds=301,
                ),
            )
        )


def test_replanning_guidance_preserves_security() -> None:
    guidance = ServicesAgent().replan_guidance(FailureKind.PERMISSION)

    assert "não tente sudo" in guidance
