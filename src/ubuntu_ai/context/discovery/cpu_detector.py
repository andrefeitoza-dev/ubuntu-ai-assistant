from __future__ import annotations

import platform


class CpuDetector:
    """Obtém informações básicas da CPU."""

    def detect(self) -> str:
        processor = platform.processor().strip()
        return processor or platform.machine()
