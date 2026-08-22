from __future__ import annotations

import platform
from pathlib import Path


class OperatingSystemDetector:
    def detect(self) -> str:
        try:
            values = self._read_os_release(Path("/etc/os-release"))
        except OSError:
            values = {}
        if values.get("PRETTY_NAME"):
            return values["PRETTY_NAME"]
        return platform.platform()

    @staticmethod
    def _read_os_release(path: Path) -> dict[str, str]:
        values: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8").splitlines():
            if "=" not in line or line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            values[key] = value.strip().strip('"')
        return values
