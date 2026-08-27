from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel


@dataclass(frozen=True, slots=True)
class DesktopAction:
    title: str
    description: str
    command: tuple[str, ...]


class SafeDesktopActionPlanner:
    """Planeja aberturas locais sem shell e com destinos validados."""

    _FOLDER = re.compile(
        r"^abra\s+(?:(?:a|minha)\s+)?pasta\s+(.+)$",
        re.IGNORECASE,
    )
    _FILE = re.compile(r"^abra\s+(?:o\s+)?arquivo\s+(.+)$", re.IGNORECASE)
    _SITE = re.compile(
        r"^(?:abra|acesse)\s+(?:(?:o\s+)?site\s+)?(https?://\S+|www\.\S+|\S+\.\S+)$",
        re.IGNORECASE,
    )
    _APPLICATION = re.compile(
        r"^(?:abra|inicie|execute)\s+(?:(?:o|a|os|as)\s+)?(.+)$",
        re.IGNORECASE,
    )
    _EMAIL = re.compile(
        r"^(?:abra|acesse)\s+(?:o\s+)?(?:meu\s+)?e-?mail$",
        re.IGNORECASE,
    )
    _APPLICATIONS = {
        "firefox": "firefox",
        "navegador firefox": "firefox",
        "arquivos": "org.gnome.Nautilus",
        "gerenciador de arquivos": "org.gnome.Nautilus",
        "terminal": "org.gnome.Terminal",
        "calculadora": "org.gnome.Calculator",
        "configuracoes": "org.gnome.Settings",
        "configurações": "org.gnome.Settings",
        "configuracoes de rede": "gnome-network-panel",
        "configurações de rede": "gnome-network-panel",
        "visual studio code": "code",
        "vs code": "code",
        "vscode": "code",
    }

    def __init__(self, home: Path | None = None) -> None:
        self._home = (home or Path.home()).expanduser().resolve()

    def try_create_plan(self, request: str) -> Plan | None:
        action = self.resolve(request)
        if action is None:
            return None
        plan = Plan(
            goal=action.title,
            estimated_seconds=1,
            risk=RiskLevel.LOW,
            planner="builtin",
        )
        plan.add_step(
            PlanStep(
                title=action.title,
                description=action.description,
                command=list(action.command),
            )
        )
        return plan

    def resolve(self, request: str) -> DesktopAction | None:
        value = self._request_value(request)
        folder = self._FOLDER.fullmatch(value)
        if folder is not None:
            path = self._safe_path(folder.group(1), expected="directory")
            if path is None:
                return None
            return DesktopAction(
                "Abrir pasta",
                f"Abre a pasta validada {path}.",
                ("xdg-open", str(path)),
            )

        file = self._FILE.fullmatch(value)
        if file is not None:
            path = self._safe_path(file.group(1), expected="file")
            if path is None:
                return None
            return DesktopAction(
                "Abrir arquivo",
                f"Abre o arquivo validado {path} no aplicativo padrão.",
                ("xdg-open", str(path)),
            )

        site = self._SITE.fullmatch(value)
        if site is not None:
            url = self._safe_url(site.group(1))
            if url is None:
                return None
            return DesktopAction(
                "Abrir site",
                f"Abre o endereço HTTPS/HTTP validado {url}.",
                ("xdg-open", url),
            )

        application = self._APPLICATION.fullmatch(value)
        if application is not None:
            app_id = self._APPLICATIONS.get(application.group(1).strip().casefold())
            if app_id is not None:
                return DesktopAction(
                    "Abrir aplicativo",
                    "Inicia um aplicativo conhecido do Ubuntu.",
                    ("gtk-launch", app_id),
                )
        return None

    def rejection_reason(self, request: str) -> str | None:
        value = self._request_value(request)
        if self._EMAIL.fullmatch(value):
            return (
                "Seu pedido é ambíguo: informe se deseja abrir um cliente de e-mail "
                "instalado ou um webmail específico."
            )
        if self.resolve(request) is not None:
            return None
        if self._FOLDER.fullmatch(value) or self._FILE.fullmatch(value):
            return (
                "Não foi possível abrir o caminho. Ele deve existir dentro da sua pasta "
                "pessoal e estar acessível ao usuário atual."
            )
        if self._SITE.fullmatch(value):
            return "Site não aberto. Somente endereços HTTP ou HTTPS válidos são permitidos."
        if self._APPLICATION.fullmatch(value):
            return "Aplicativo não aberto. Informe um aplicativo Ubuntu conhecido e confiável."
        return None

    def has_desktop_intent(self, request: str) -> bool:
        value = self._request_value(request)
        return any(
            pattern.fullmatch(value) is not None
            for pattern in (
                self._FOLDER,
                self._FILE,
                self._SITE,
                self._EMAIL,
                self._APPLICATION,
            )
        )

    @staticmethod
    def _request_value(request: str) -> str:
        value = request.strip()
        if value.endswith("."):
            return value[:-1].rstrip()
        return value

    def _safe_path(self, raw_value: str, *, expected: str) -> Path | None:
        value = raw_value.strip().strip("\"'")
        if not value or any(character in value for character in ";|`\n\r\x00"):
            return None
        standard_folder = self._standard_folder(value)
        candidate = standard_folder if standard_folder is not None else Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = self._home / candidate
        try:
            resolved = candidate.resolve(strict=True)
            resolved.relative_to(self._home)
        except (OSError, RuntimeError, ValueError):
            return None
        if expected == "directory" and not resolved.is_dir():
            return None
        if expected == "file" and not resolved.is_file():
            return None
        required = os.R_OK | (os.X_OK if expected == "directory" else 0)
        return resolved if os.access(resolved, required) else None

    def _standard_folder(self, value: str) -> Path | None:
        if value.casefold() not in {"documentos", "documents"}:
            return None

        candidates: list[Path] = []
        config = self._home / ".config" / "user-dirs.dirs"

        try:
            lines = config.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []

        prefix = "XDG_DOCUMENTS_DIR="
        for line in lines:
            if not line.startswith(prefix):
                continue
            configured = line.removeprefix(prefix).strip().strip('"')
            configured = configured.replace(
                "$HOME",
                str(self._home),
                1,
            )
            candidates.append(Path(configured).expanduser())
            break

        candidates.extend(
            (
                self._home / "Documentos",
                self._home / "Documents",
            )
        )

        for candidate in candidates:
            try:
                resolved = candidate.resolve(strict=True)
                resolved.relative_to(self._home)
            except (OSError, RuntimeError, ValueError):
                continue
            if resolved.is_dir():
                return resolved

        return None

    @staticmethod
    def _safe_url(raw_value: str) -> str | None:
        value = raw_value.strip().rstrip(".,")
        if "://" not in value:
            value = f"https://{value}"
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            return None
        if parsed.username or parsed.password:
            return None
        try:
            parsed.port
        except ValueError:
            return None
        return parsed.geturl()
