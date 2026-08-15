from __future__ import annotations

import socket


class HostnameDetector:
    def detect(self) -> str:
        return socket.gethostname()
