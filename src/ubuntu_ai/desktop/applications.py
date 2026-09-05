from __future__ import annotations

import configparser
import os
import re
import shlex
import unicodedata
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DesktopApplication:
    desktop_id: str
    name: str
    source: Path


class DesktopApplicationCatalog:
    """Descobre entradas de aplicativos em diretórios de sistema confiáveis."""

    DEFAULT_ROOTS = (
        Path("/usr/local/share/applications"),
        Path("/usr/share/applications"),
        Path("/var/lib/snapd/desktop/applications"),
    )
    _UNSAFE_EXECUTABLES = frozenset(
        {
            "bash",
            "dash",
            "env",
            "pkexec",
            "python",
            "python3",
            "sh",
            "sudo",
        }
    )
    _SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")

    def __init__(self, roots: tuple[Path, ...] | None = None) -> None:
        selected_roots = self.DEFAULT_ROOTS if roots is None else roots
        self._roots = tuple(root.resolve() for root in selected_roots)
        self._require_readonly_roots = roots is None
        self._applications: tuple[DesktopApplication, ...] | None = None

    @property
    def applications(self) -> tuple[DesktopApplication, ...]:
        if self._applications is None:
            discovered: list[DesktopApplication] = []
            for root in self._roots:
                discovered.extend(self._read_root(root))
            self._applications = tuple(discovered)
        return self._applications

    def find(self, label: str) -> DesktopApplication | None:
        normalized = self._normalize(label)
        exact_matches = {
            application
            for application in self.applications
            if normalized
            in {
                self._normalize(application.name),
                self._normalize(application.desktop_id),
            }
        }
        if len(exact_matches) == 1:
            return next(iter(exact_matches))
        partial_matches = {
            application
            for application in self.applications
            if self._normalize(application.name).startswith(f"{normalized} ")
        }
        return next(iter(partial_matches)) if len(partial_matches) == 1 else None

    def contains_id(self, desktop_id: str) -> bool:
        return any(application.desktop_id == desktop_id for application in self.applications)

    def _read_root(self, root: Path) -> list[DesktopApplication]:
        if not root.is_dir():
            return []
        if self._require_readonly_roots and os.access(root, os.W_OK):
            return []
        applications: list[DesktopApplication] = []
        try:
            entries = sorted(root.glob("*.desktop"))
        except OSError:
            return []
        for path in entries:
            application = self._read_entry(root, path)
            if application is not None:
                applications.append(application)
        return applications

    def _read_entry(self, root: Path, path: Path) -> DesktopApplication | None:
        try:
            resolved = path.resolve(strict=True)
            resolved.relative_to(root)
            stat = resolved.stat()
        except (OSError, RuntimeError, ValueError):
            return None
        if not resolved.is_file() or stat.st_mode & 0o022:
            return None
        desktop_id = resolved.stem
        if self._SAFE_ID.fullmatch(desktop_id) is None:
            return None

        parser = configparser.ConfigParser(interpolation=None, strict=False)
        parser.optionxform = str
        try:
            parser.read(resolved, encoding="utf-8")
            entry = parser["Desktop Entry"]
        except (OSError, UnicodeError, configparser.Error, KeyError):
            return None
        if entry.get("Type") != "Application":
            return None
        if self._true(entry.get("Hidden")) or self._true(entry.get("NoDisplay")):
            return None

        name = entry.get("Name[pt_BR]") or entry.get("Name[pt]") or entry.get("Name")
        exec_value = entry.get("Exec")
        if not name or not exec_value or not self._safe_exec(exec_value):
            return None
        try_exec = entry.get("TryExec")
        if try_exec and not self._safe_executable(try_exec):
            return None
        return DesktopApplication(desktop_id, name.strip(), resolved)

    @classmethod
    def _safe_exec(cls, value: str) -> bool:
        if any(ord(character) < 32 for character in value):
            return False
        try:
            arguments = shlex.split(value)
        except ValueError:
            return False
        if not arguments or not cls._safe_executable(arguments[0]):
            return False
        return not any(argument in {";", "&&", "||", "|"} for argument in arguments[1:])

    @classmethod
    def _safe_executable(cls, value: str) -> bool:
        executable = Path(value).name
        return bool(executable) and executable not in cls._UNSAFE_EXECUTABLES

    @staticmethod
    def _true(value: str | None) -> bool:
        return value is not None and value.strip().casefold() == "true"

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.encode("ascii", "ignore").decode().lower()
        normalized = re.sub(r"[^a-z0-9]+", " ", normalized)
        return " ".join(normalized.split())
