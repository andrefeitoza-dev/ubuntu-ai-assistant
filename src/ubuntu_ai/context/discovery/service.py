from __future__ import annotations

from ubuntu_ai.context.discovery.cpu_detector import CpuDetector
from ubuntu_ai.context.discovery.disk_detector import DiskDetector
from ubuntu_ai.context.discovery.docker_detector import DockerDetector
from ubuntu_ai.context.discovery.git_detector import GitDetector
from ubuntu_ai.context.discovery.hostname_detector import HostnameDetector
from ubuntu_ai.context.discovery.kernel_detector import KernelDetector
from ubuntu_ai.context.discovery.memory_detector import MemoryDetector
from ubuntu_ai.context.discovery.models import EnvironmentSnapshot
from ubuntu_ai.context.discovery.ollama_detector import OllamaDetector
from ubuntu_ai.context.discovery.os_detector import OperatingSystemDetector
from ubuntu_ai.context.discovery.project_detector import ProjectDetector
from ubuntu_ai.context.discovery.python_detector import PythonDetector


class ContextDiscoveryService:
    """Descobre automaticamente informações do ambiente."""

    def __init__(
        self,
        git: GitDetector | None = None,
        project: ProjectDetector | None = None,
        python: PythonDetector | None = None,
        docker: DockerDetector | None = None,
        ollama: OllamaDetector | None = None,
        cpu: CpuDetector | None = None,
        memory: MemoryDetector | None = None,
        disk: DiskDetector | None = None,
        hostname: HostnameDetector | None = None,
        kernel: KernelDetector | None = None,
        operating_system: OperatingSystemDetector | None = None,
    ) -> None:
        self._git = git or GitDetector()
        self._project = project or ProjectDetector()
        self._python = python or PythonDetector()
        self._docker = docker or DockerDetector()
        self._ollama = ollama or OllamaDetector()

        self._cpu = cpu or CpuDetector()
        self._memory = memory or MemoryDetector()
        self._disk = disk or DiskDetector()
        self._hostname = hostname or HostnameDetector()
        self._kernel = kernel or KernelDetector()
        self._operating_system = operating_system or OperatingSystemDetector()

    def discover(
        self,
        working_directory: str,
    ) -> EnvironmentSnapshot:
        return EnvironmentSnapshot(
            working_directory=working_directory,
            project_name=self._project.detect(working_directory),
            git_repository=self._git.is_repository(working_directory),
            git_branch=self._git.branch(working_directory),
            python_version=self._python.version(),
            virtual_environment=self._python.virtual_environment(),
            docker_available=self._docker.available(),
            ollama_available=self._ollama.available(),
            operating_system=self._operating_system.detect(),
            cpu=self._cpu.detect(),
            memory_mb=self._memory.detect(),
            disk_gb=self._disk.detect(),
            hostname=self._hostname.detect(),
            kernel=self._kernel.detect(),
        )
