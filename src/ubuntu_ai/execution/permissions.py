from __future__ import annotations

import shlex
from threading import Lock


class CapabilityPermissions:
    """Restrições adicionais da sessão; nunca substituem a política central."""

    _EXECUTABLES = {
        "desktop": frozenset({"firefox", "gtk-launch", "xdg-open"}),
        "files": frozenset({"find", "ls", "du", "mkdir", "cp", "mv", "gio"}),
        "system": frozenset({"df", "free", "ip", "lsblk", "ps", "uname"}),
        "services": frozenset({"journalctl", "systemctl"}),
        "packages": frozenset({"apt", "apt-get", "dpkg"}),
    }

    def __init__(self) -> None:
        self._denied: set[str] = set()
        self._lock = Lock()

    @property
    def denied(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._denied))

    def set_allowed(self, capability: str, *, allowed: bool) -> None:
        if capability not in self._EXECUTABLES:
            raise ValueError("Capacidade desconhecida.")
        with self._lock:
            if allowed:
                self._denied.discard(capability)
            else:
                self._denied.add(capability)

    def denial_reason(self, command: str) -> str | None:
        try:
            executable = shlex.split(command)[0]
        except (ValueError, IndexError):
            return None
        with self._lock:
            for capability in self._denied:
                if executable in self._EXECUTABLES[capability]:
                    return f"Capacidade '{capability}' desativada pelo usuário nesta sessão."
        return None


capability_permissions = CapabilityPermissions()
