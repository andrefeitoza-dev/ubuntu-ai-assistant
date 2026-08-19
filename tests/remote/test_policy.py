import pytest

from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteHost,
    RemoteHostKind,
)
from ubuntu_ai.remote.policy import RemoteExecutionPolicy


def ssh_host() -> RemoteHost:
    return RemoteHost(
        name="server",
        kind=RemoteHostKind.SSH,
        hostname="server.local",
    )


def test_destructive_command_requires_confirmation() -> None:
    decision = RemoteExecutionPolicy().evaluate(
        ssh_host(),
        RemoteCommand(("reboot",)),
    )

    assert decision.allowed
    assert decision.requires_confirmation
    assert decision.risk is RiskLevel.CRITICAL


@pytest.mark.parametrize(
    "command",
    (
        ("sudo", "id"),
        ("su", "-c", "id"),
        ("bash", "-lc", "id"),
    ),
)
def test_policy_blocks_elevation_and_shell_wrappers(
    command: tuple[str, ...],
) -> None:
    decision = RemoteExecutionPolicy().evaluate(
        ssh_host(),
        RemoteCommand(command),
    )

    assert not decision.allowed
    assert not decision.requires_confirmation
    assert decision.risk is RiskLevel.CRITICAL


def test_remote_read_only_command_is_low_risk() -> None:
    decision = RemoteExecutionPolicy().evaluate(
        ssh_host(),
        RemoteCommand(("free", "-m")),
    )

    assert decision.allowed
    assert not decision.requires_confirmation
    assert decision.risk is RiskLevel.LOW


def test_unknown_remote_action_is_high_risk_and_requires_confirmation() -> None:
    decision = RemoteExecutionPolicy().evaluate(
        ssh_host(),
        RemoteCommand(("apt", "install", "example")),
    )

    assert decision.allowed
    assert decision.requires_confirmation
    assert decision.risk is RiskLevel.HIGH


def test_reversible_remote_action_is_medium_risk() -> None:
    decision = RemoteExecutionPolicy().evaluate(
        RemoteHost(name="server", kind=RemoteHostKind.SSH, hostname="server.local"),
        RemoteCommand(("mkdir", "/tmp/example")),
    )

    assert decision.allowed
    assert decision.requires_confirmation
    assert decision.risk is RiskLevel.MEDIUM


@pytest.mark.parametrize("operation", ("status", "show", "is-active", "--failed"))
def test_systemctl_read_operations_are_low_risk(operation: str) -> None:
    decision = RemoteExecutionPolicy().evaluate(
        RemoteHost(name="server", kind=RemoteHostKind.SSH, hostname="server.local"),
        RemoteCommand(("systemctl", operation, "ssh")),
    )

    assert decision.risk is RiskLevel.LOW
    assert not decision.requires_confirmation


@pytest.mark.parametrize("operation", ("start", "stop", "restart", "enable", "disable"))
def test_systemctl_mutations_are_high_risk(operation: str) -> None:
    decision = RemoteExecutionPolicy().evaluate(
        RemoteHost(name="server", kind=RemoteHostKind.SSH, hostname="server.local"),
        RemoteCommand(("systemctl", operation, "ssh")),
    )

    assert decision.risk is RiskLevel.HIGH
    assert decision.requires_confirmation
