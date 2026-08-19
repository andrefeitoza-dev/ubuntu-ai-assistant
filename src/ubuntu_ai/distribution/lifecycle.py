from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from enum import StrEnum
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from ubuntu_ai.config.defaults import (
    default_cache_directory,
    default_config_directory,
    default_data_directory,
    default_state_directory,
)
from ubuntu_ai.version import PACKAGE_NAME

_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:[a-zA-Z0-9.-]+)?$")
_WHEEL = re.compile(r"^ubuntu_ai_assistant-[A-Za-z0-9_.+-]+-py3-none-any\.whl$")


def lifecycle_user_paths(home: Path) -> tuple[Path, Path, Path]:
    """Calcula artefatos do launcher sem acoplar distribuição à GUI."""

    launcher = home / ".local" / "bin" / PACKAGE_NAME
    desktop = home / ".local" / "share" / "applications" / f"{PACKAGE_NAME}.desktop"
    icon = (
        home / ".local" / "share" / "icons" / "hicolor" / "512x512" / "apps" / f"{PACKAGE_NAME}.png"
    )
    return launcher, desktop, icon


class LifecycleOperation(StrEnum):
    INSTALL = "install"
    UPDATE = "update"
    UNINSTALL = "uninstall"


@dataclass(frozen=True, slots=True)
class LifecyclePlan:
    operation: LifecycleOperation
    command: tuple[str, ...]
    description: str


@dataclass(frozen=True, slots=True)
class LifecycleResult:
    plan: LifecyclePlan
    return_code: int
    stdout: str
    stderr: str

    @property
    def success(self) -> bool:
        return self.return_code == 0


@dataclass(frozen=True, slots=True)
class LifecycleStatus:
    version: str | None
    command_available: bool
    gui_available: bool
    launcher_installed: bool
    desktop_installed: bool
    icon_installed: bool
    preserved_directories: tuple[Path, ...]

    @property
    def healthy(self) -> bool:
        return all(
            (
                self.version is not None,
                self.command_available,
                self.gui_available,
                self.launcher_installed,
                self.desktop_installed,
                self.icon_installed,
            )
        )


class LifecycleManager:
    """Planeja e executa o ciclo de vida sem shell ou elevação automática."""

    def __init__(self, *, uv_executable: str | None = None, home: Path | None = None) -> None:
        executable = uv_executable or shutil.which("uv")
        if not executable:
            raise RuntimeError("O comando uv é necessário para gerenciar a instalação isolada.")
        self._uv = str(Path(executable).expanduser())
        self._home = (home or Path.home()).expanduser()

    def status(self) -> LifecycleStatus:
        try:
            installed_version = version(PACKAGE_NAME)
        except PackageNotFoundError:
            installed_version = None

        launcher, desktop, icon = lifecycle_user_paths(self._home)
        return LifecycleStatus(
            version=installed_version,
            command_available=shutil.which("ubuntu-ai") is not None,
            gui_available=shutil.which("ubuntu-ai-gui") is not None,
            launcher_installed=launcher.is_file(),
            desktop_installed=desktop.is_file(),
            icon_installed=icon.is_file(),
            preserved_directories=self.preserved_directories(),
        )

    @staticmethod
    def preserved_directories() -> tuple[Path, ...]:
        return (
            default_config_directory(),
            default_data_directory(),
            default_state_directory(),
            default_cache_directory(),
        )

    def install_plan(self, source: str | None = None) -> LifecyclePlan:
        package = self._validated_source(source)
        return LifecyclePlan(
            operation=LifecycleOperation.INSTALL,
            command=(self._uv, "tool", "install", package),
            description=f"Instalar {package} em ambiente isolado.",
        )

    def update_plan(
        self,
        version_value: str | None = None,
        wheel: str | None = None,
    ) -> LifecyclePlan:
        if version_value is not None and wheel is not None:
            raise ValueError("Informe uma versão ou um wheel, nunca os dois.")

        package = self._validated_source(wheel) if wheel is not None else PACKAGE_NAME
        if version_value is not None:
            normalized = version_value.strip()
            if not _VERSION.fullmatch(normalized):
                raise ValueError("Versão inválida. Use o formato 1.6.0, 1.6.0rc1 ou equivalente.")
            package = f"{PACKAGE_NAME}=={normalized}"
        return LifecyclePlan(
            operation=LifecycleOperation.UPDATE,
            command=(self._uv, "tool", "install", "--force", package),
            description=f"Atualizar a instalação isolada usando {package}.",
        )

    def uninstall_plan(self) -> LifecyclePlan:
        return LifecyclePlan(
            operation=LifecycleOperation.UNINSTALL,
            command=(self._uv, "tool", "uninstall", PACKAGE_NAME),
            description="Remover o pacote preservando configurações, dados e histórico.",
        )

    @staticmethod
    def execute(plan: LifecyclePlan) -> LifecycleResult:
        completed = subprocess.run(
            plan.command,
            check=False,
            capture_output=True,
            text=True,
            shell=False,
        )
        return LifecycleResult(
            plan=plan,
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    @staticmethod
    def _validated_source(source: str | None) -> str:
        if source is None:
            return PACKAGE_NAME
        normalized = source.strip()
        if not normalized:
            raise ValueError("A origem do pacote não pode estar vazia.")
        path = Path(normalized).expanduser()
        if not path.is_absolute():
            raise ValueError("O wheel deve usar caminho absoluto.")
        if not path.is_file() or not _WHEEL.fullmatch(path.name):
            raise ValueError("Informe um wheel válido do Ubuntu AI Assistant.")
        return str(path.resolve())
