from __future__ import annotations

from ubuntu_ai.remote.docker_executor import DockerExecutor
from ubuntu_ai.remote.local_executor import LocalExecutor
from ubuntu_ai.remote.models import (
    RemoteCommand,
    RemoteExecutionResult,
    RemoteHostKind,
)
from ubuntu_ai.remote.policy import RemoteExecutionPolicy
from ubuntu_ai.remote.registry import RemoteHostRegistry
from ubuntu_ai.remote.ssh_executor import SSHExecutor


class RemoteConfirmationRequired(RuntimeError):
    """Sinaliza que a política exige confirmação explícita."""


class RemoteExecutionEngine:
    """Fachada para execução local, SSH e Docker com política comum."""

    def __init__(
        self,
        registry: RemoteHostRegistry,
        *,
        local_executor: LocalExecutor | None = None,
        ssh_executor: SSHExecutor | None = None,
        docker_executor: DockerExecutor | None = None,
        policy: RemoteExecutionPolicy | None = None,
    ) -> None:
        self._registry = registry
        self._local = local_executor or LocalExecutor()
        self._ssh = ssh_executor or SSHExecutor()
        self._docker = docker_executor or DockerExecutor()
        self._policy = policy or RemoteExecutionPolicy()

    def execute(
        self,
        host_name: str,
        command: RemoteCommand,
        *,
        confirmed: bool = False,
    ) -> RemoteExecutionResult:
        host = self._registry.get(host_name)
        decision = self._policy.evaluate(host, command)

        if not decision.allowed:
            raise PermissionError(decision.reason)

        if decision.requires_confirmation and not confirmed:
            raise RemoteConfirmationRequired(decision.reason)

        if host.kind is RemoteHostKind.LOCAL:
            return self._local.execute(host, command)

        if host.kind is RemoteHostKind.SSH:
            return self._ssh.execute(host, command)

        if host.kind is RemoteHostKind.DOCKER:
            return self._docker.execute(host, command)

        raise ValueError(f"Tipo de host não suportado: {host.kind}")
