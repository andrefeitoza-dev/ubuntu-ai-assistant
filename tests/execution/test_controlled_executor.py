from unittest.mock import Mock

from ubuntu_ai.execution.controlled_executor import ControlledExecutor
from ubuntu_ai.execution.default_policy import DefaultExecutionPolicy
from ubuntu_ai.execution.mode import ExecutionMode
from ubuntu_ai.execution.models import (
    ExecutionRequest,
    ExecutionResult,
    ExecutionStatus,
)
from ubuntu_ai.execution.permissions import CapabilityPermissions
from ubuntu_ai.execution.system_executor import SystemExecutor


def test_executor_approves_safe_command_without_system_executor() -> None:
    executor = ControlledExecutor(DefaultExecutionPolicy())

    result = executor.execute(ExecutionRequest(command="pwd"))

    assert result.status is ExecutionStatus.APPROVED
    assert result.message == "Comando autorizado."
    assert result.command == "pwd"


def test_executor_blocks_rm() -> None:
    executor = ControlledExecutor(DefaultExecutionPolicy())

    result = executor.execute(ExecutionRequest(command="rm -rf /"))

    assert result.status is ExecutionStatus.BLOCKED
    assert "bloqueado" in result.message
    assert result.command == "rm -rf /"


def test_executor_blocks_empty_command() -> None:
    executor = ControlledExecutor(DefaultExecutionPolicy())

    result = executor.execute(ExecutionRequest(command=""))

    assert result.status is ExecutionStatus.BLOCKED
    assert result.command == ""


def test_executor_delegates_authorized_command_to_system_executor() -> None:
    system_executor = Mock(spec=SystemExecutor)
    system_executor.execute.return_value = ExecutionResult(
        status=ExecutionStatus.EXECUTED,
        message="Comando executado com sucesso.",
        command="pwd",
        return_code=0,
        stdout="/home/user/project",
    )

    executor = ControlledExecutor(
        policy=DefaultExecutionPolicy(),
        system_executor=system_executor,
    )

    request = ExecutionRequest(command="pwd")
    result = executor.execute(request)

    assert result.status is ExecutionStatus.EXECUTED
    assert result.command == "pwd"
    assert result.return_code == 0
    assert result.stdout == "/home/user/project"
    assert result.policy_reason == "Comando autorizado."

    system_executor.execute.assert_called_once_with(request)


def test_executor_does_not_delegate_blocked_command() -> None:
    system_executor = Mock(spec=SystemExecutor)

    executor = ControlledExecutor(
        policy=DefaultExecutionPolicy(),
        system_executor=system_executor,
    )

    result = executor.execute(ExecutionRequest(command="rm -rf /"))

    assert result.status is ExecutionStatus.BLOCKED
    assert result.command == "rm -rf /"
    assert result.policy_reason is not None

    system_executor.execute.assert_not_called()


def test_global_simulation_validates_policy_but_forces_dry_run() -> None:
    system_executor = Mock(spec=SystemExecutor)
    system_executor.execute.return_value = ExecutionResult(
        status=ExecutionStatus.APPROVED,
        message="Comando aprovado em modo de simulação.",
    )
    mode = ExecutionMode()
    mode.set_simulation(True)
    executor = ControlledExecutor(
        DefaultExecutionPolicy(),
        system_executor=system_executor,
        mode=mode,
    )

    result = executor.execute(ExecutionRequest(command="pwd"))

    assert result.status is ExecutionStatus.APPROVED
    simulated = system_executor.execute.call_args.args[0]
    assert simulated.command == "pwd"
    assert simulated.dry_run is True


def test_global_simulation_does_not_bypass_policy() -> None:
    system_executor = Mock(spec=SystemExecutor)
    mode = ExecutionMode()
    mode.set_simulation(True)
    executor = ControlledExecutor(
        DefaultExecutionPolicy(),
        system_executor=system_executor,
        mode=mode,
    )

    result = executor.execute(ExecutionRequest(command="rm -rf /"))

    assert result.status is ExecutionStatus.BLOCKED
    system_executor.execute.assert_not_called()


def test_capability_permission_can_additionally_block_desktop_actions() -> None:
    system_executor = Mock(spec=SystemExecutor)
    permissions = CapabilityPermissions()
    permissions.set_allowed("desktop", allowed=False)
    executor = ControlledExecutor(
        DefaultExecutionPolicy(),
        system_executor=system_executor,
        permissions=permissions,
    )

    result = executor.execute(ExecutionRequest(command="xdg-open https://github.com"))

    assert result.status is ExecutionStatus.BLOCKED
    assert "desktop" in result.message
    system_executor.execute.assert_not_called()


def test_capability_permission_never_allows_centrally_blocked_command() -> None:
    permissions = CapabilityPermissions()
    permissions.set_allowed("files", allowed=True)
    executor = ControlledExecutor(DefaultExecutionPolicy(), permissions=permissions)

    assert executor.execute(ExecutionRequest(command="rm -rf /")).status is ExecutionStatus.BLOCKED


def test_package_permission_applies_through_pkexec_wrapper() -> None:
    permissions = CapabilityPermissions()
    permissions.set_allowed("packages", allowed=False)
    executor = ControlledExecutor(DefaultExecutionPolicy(), permissions=permissions)

    result = executor.execute(ExecutionRequest(command="pkexec apt-get update"))

    assert result.status is ExecutionStatus.BLOCKED
    assert "packages" in result.message
