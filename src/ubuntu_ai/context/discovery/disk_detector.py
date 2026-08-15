from __future__ import annotations

import shutil


class DiskDetector:
    """Obtém o espaço total do disco."""

    def detect(self, path: str = "/") -> int | None:
        try:
            usage = shutil.disk_usage(path)
            return usage.total // (1024 * 1024 * 1024)
        except Exception:
            return None
