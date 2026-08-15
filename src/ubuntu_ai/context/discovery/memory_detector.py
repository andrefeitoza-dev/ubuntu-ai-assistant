from __future__ import annotations

import os


class MemoryDetector:
    """Obtém a memória total do sistema."""

    def detect(self) -> int | None:
        try:
            pages = os.sysconf("SC_PHYS_PAGES")
            page_size = os.sysconf("SC_PAGE_SIZE")
            return (pages * page_size) // (1024 * 1024)
        except Exception:
            return None
