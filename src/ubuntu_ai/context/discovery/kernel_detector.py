from __future__ import annotations

import platform


class KernelDetector:
    def detect(self) -> str:
        return platform.release()
