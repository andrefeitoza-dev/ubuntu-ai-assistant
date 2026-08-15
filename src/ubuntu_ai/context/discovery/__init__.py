from ubuntu_ai.context.discovery.cpu_detector import CpuDetector
from ubuntu_ai.context.discovery.disk_detector import DiskDetector
from ubuntu_ai.context.discovery.docker_detector import DockerDetector
from ubuntu_ai.context.discovery.git_detector import GitDetector
from ubuntu_ai.context.discovery.hostname_detector import HostnameDetector
from ubuntu_ai.context.discovery.kernel_detector import KernelDetector
from ubuntu_ai.context.discovery.memory_detector import MemoryDetector
from ubuntu_ai.context.discovery.ollama_detector import OllamaDetector
from ubuntu_ai.context.discovery.os_detector import OperatingSystemDetector
from ubuntu_ai.context.discovery.project_detector import ProjectDetector
from ubuntu_ai.context.discovery.python_detector import PythonDetector
from ubuntu_ai.context.discovery.service import ContextDiscoveryService

__all__ = [
    "ContextDiscoveryService",
    "CpuDetector",
    "DiskDetector",
    "DockerDetector",
    "GitDetector",
    "HostnameDetector",
    "KernelDetector",
    "MemoryDetector",
    "OllamaDetector",
    "OperatingSystemDetector",
    "ProjectDetector",
    "PythonDetector",
]
