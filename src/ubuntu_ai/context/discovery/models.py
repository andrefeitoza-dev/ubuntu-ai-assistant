from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class EnvironmentSnapshot:
    """Representa o ambiente detectado pelo Ubuntu AI."""

    working_directory: str

    project_name: str | None

    git_repository: bool
    git_branch: str | None

    python_version: str | None
    virtual_environment: str | None

    docker_available: bool
    ollama_available: bool

    operating_system: str

    cpu: str | None = None
    memory_mb: int | None = None
    disk_gb: int | None = None
    hostname: str | None = None
    kernel: str | None = None
