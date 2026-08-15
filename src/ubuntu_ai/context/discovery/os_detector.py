from __future__ import annotations

import platform


class OperatingSystemDetector:
    def detect(self) -> str:
        return platform.platform()
