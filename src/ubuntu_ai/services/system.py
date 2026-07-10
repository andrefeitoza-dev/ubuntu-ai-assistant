import platform
import shutil
from dataclasses import dataclass

import psutil


@dataclass(slots=True)
class SystemInfo:
    python_version: str
    operating_system: str
    architecture: str
    cpu_cores: int
    ram_total_gb: float
    ram_available_gb: float
    git_installed: bool


class SystemService:
    """Obtém informações sobre o sistema operacional."""

    def get_info(self) -> SystemInfo:
        memory = psutil.virtual_memory()

        return SystemInfo(
            python_version=platform.python_version(),
            operating_system=platform.platform(),
            architecture=platform.machine(),
            cpu_cores=psutil.cpu_count(logical=True) or 0,
            ram_total_gb=round(memory.total / (1024**3), 2),
            ram_available_gb=round(memory.available / (1024**3), 2),
            git_installed=shutil.which("git") is not None,
        )
    