from __future__ import annotations

import re
import shutil
import subprocess
from collections.abc import Iterable

from ubuntu_ai.execution_intelligence.models import ToolEnvironment
from ubuntu_ai.tools.capability import ToolCapability

_VERSION_PATTERN = re.compile(r"\d+(?:\.\d+){0,3}")


class DiscoveryEngine:
    """Descobre executáveis e versões sem modificar o sistema."""

    def __init__(self) -> None:
        self._cache: dict[str, ToolEnvironment] = {}

    def discover_executable(
        self, executable: str, *, refresh: bool = False
    ) -> ToolEnvironment:
        key = executable.strip().lower()
        if not refresh and key in self._cache:
            return self._cache[key]

        path = shutil.which(executable)
        environment = ToolEnvironment(
            name=key,
            executable=executable,
            available=path is not None,
            path=path,
            version=self._read_version(path) if path else None,
        )
        self._cache[key] = environment
        return environment

    def discover_capability(
        self,
        capability: ToolCapability,
        *,
        refresh: bool = False,
    ) -> tuple[ToolEnvironment, ...]:
        return tuple(
            self.discover_executable(executable, refresh=refresh)
            for executable in capability.executables
        )

    def discover_all(
        self,
        capabilities: Iterable[ToolCapability],
        *,
        refresh: bool = False,
    ) -> dict[str, tuple[ToolEnvironment, ...]]:
        return {
            capability.name: self.discover_capability(capability, refresh=refresh)
            for capability in capabilities
        }

    def clear_cache(self) -> None:
        self._cache.clear()

    @staticmethod
    def _read_version(path: str) -> str | None:
        for flag in ("--version", "-V"):
            try:
                completed = subprocess.run(
                    [path, flag],
                    capture_output=True,
                    text=True,
                    timeout=2,
                    check=False,
                )
            except (OSError, subprocess.SubprocessError):
                continue
            output = f"{completed.stdout}\n{completed.stderr}"
            match = _VERSION_PATTERN.search(output)
            if match:
                return match.group(0)
        return None
