from __future__ import annotations

import os
import re
import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from ubuntu_ai.desktop import DesktopApplicationCatalog
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
    _UNSAFE_URI = re.compile(
        r"^(?:abra|acesse)\s+(?:o\s+site\s+)?[a-z][a-z0-9+.-]*:",
        re.IGNORECASE,
    )
    _SITE_IN_BROWSER = re.compile(
        r"^(?:abra|acesse)\s+(?:o\s+)?(?:site\s+)?"
        r"(.+?)\s+(?:no|na)\s+(firefox)$",
        re.IGNORECASE,
    )
    _SITE_ALIAS = re.compile(
        r"^(?:abra|acesse)\s+(?:(?:o|a)\s+)?(?:site\s+)?(?:(?:do|da)\s+)?(.+)$",
        re.IGNORECASE,
    )
    _EXPLICIT_NAMED_SITE = re.compile(r"^(?:abra|acesse)\s+(?:(?:o|a)\s+)?site\s+", re.IGNORECASE)
    _SITE_ALIASES = {
        "github": "https://github.com",
        "receita": "https://www.gov.br/receitafederal/pt-br",
        "receita federal": "https://www.gov.br/receitafederal/pt-br",
        "ubuntu": "https://ubuntu.com",
    }
    _BROWSERS = {
        "firefox": "firefox",
    }
    _APPLICATION = re.compile(
        r"^(?:abra|inicie|execute)\s+(?:(?:o|a|os|as)\s+)?(.+)$",
        re.IGNORECASE,
    )
    _EMAIL = re.compile(
        r"^(?:abra|acesse)\s+(?:o\s+)?(?:meu\s+)?e-?mail$",
        re.IGNORECASE,
    )
    _APPLICATIONS = {
        "calculator": "org.gnome.Calculator",
        "firefox": "firefox",
        "libreoffice": "libreoffice-startcenter",
        "libre office": "libreoffice-startcenter",
        "navegador firefox": "firefox",
        "arquivos": "org.gnome.Nautilus",
        "gerenciador de arquivos": "org.gnome.Nautilus",
        "terminal": "org.gnome.Terminal",
        "calculadora": "org.gnome.Calculator",
        "configuracoes": "org.gnome.Settings",
        "configurações": "org.gnome.Settings",
        "configuracoes de rede": "gnome-network-panel",
        "configurações de rede": "gnome-network-panel",
        "painel de rede": "gnome-network-panel",
        "visual studio code": "code",
        "vs code": "code",
        "vscode": "code",
    }
    _GENERIC_BROWSER = frozenset({"navegador", "browser"})
    _DEFAULT_BROWSER = frozenset(
        {"navegador padrao", "navegador padrão", "browser padrao", "browser padrão"}
    )

    _STANDARD_FOLDERS = {
        "documentos": ("DOCUMENTS", ("Documentos", "Documents")),
        "documents": ("DOCUMENTS", ("Documents", "Documentos")),
        "downloads": ("DOWNLOAD", ("Downloads",)),
        "download": ("DOWNLOAD", ("Downloads",)),
        "imagens": ("PICTURES", ("Imagens", "Pictures")),
        "pictures": ("PICTURES", ("Pictures", "Imagens")),
        "musica": ("MUSIC", ("Música", "Music")),
        "music": ("MUSIC", ("Music", "Música")),
        "videos": ("VIDEOS", ("Vídeos", "Videos")),
        "area de trabalho": ("DESKTOP", ("Área de Trabalho", "Desktop")),
        "desktop": ("DESKTOP", ("Desktop", "Área de Trabalho")),
    }

    def __init__(
        self,
        home: Path | None = None,
        applications: DesktopApplicationCatalog | None = None,
    ) -> None:
        self._home = (home or Path.home()).expanduser().resolve()
        self._applications = applications or DesktopApplicationCatalog()

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
        browser_site = self._SITE_IN_BROWSER.fullmatch(value)
        if browser_site is not None:
            raw_target = browser_site.group(1).strip()
            alias = self._normalize_label(raw_target)
            target = self._SITE_ALIASES.get(alias, raw_target)
            url = self._safe_url(target)
            browser = self._BROWSERS.get(browser_site.group(2).strip().casefold())
            if url is None or browser is None:
                return None
            return DesktopAction(
                "Abrir site no navegador",
                f"Abre o endereço validado {url} no Firefox.",
                (browser, url),
            )

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

        site_alias = self._SITE_ALIAS.fullmatch(value)
        if site_alias is not None:
            alias = self._normalize_label(site_alias.group(1))
            url = self._SITE_ALIASES.get(alias)
            if url is not None:
                return DesktopAction(
                    "Abrir site",
                    f"Abre o endereço validado {url} no navegador padrão.",
                    ("xdg-open", url),
                )

        application = self._APPLICATION.fullmatch(value)
        if application is not None:
            app_name = application.group(1).strip().casefold()
            if app_name in self._GENERIC_BROWSER | self._DEFAULT_BROWSER:
                default_browser = self._default_browser()
                if default_browser is None:
                    return None
                return DesktopAction(
                    "Abrir navegador padrão",
                    "Inicia o navegador padrão configurado no Ubuntu.",
                    ("gtk-launch", default_browser),
                )
            folder = self._standard_folder(app_name)
            if folder is not None:
                return DesktopAction(
                    "Abrir pasta",
                    f"Abre a pasta padrão validada {folder}.",
                    ("xdg-open", str(folder)),
                )
            app_id = self._APPLICATIONS.get(app_name)
            if app_id is not None:
                return DesktopAction(
                    "Abrir aplicativo",
                    "Inicia um aplicativo conhecido do Ubuntu.",
                    ("gtk-launch", app_id),
                )
            discovered = self._applications.find(app_name)
            if discovered is not None:
                return DesktopAction(
                    "Abrir aplicativo",
                    (
                        "Inicia o aplicativo validado "
                        f"{discovered.name} a partir de uma entrada de sistema confiável."
                    ),
                    ("gtk-launch", discovered.desktop_id),
                )
        return None

    def _default_browser(self) -> str | None:
        try:
            result = subprocess.run(
                ("xdg-settings", "get", "default-web-browser"),
                capture_output=True,
                check=False,
                text=True,
                timeout=2,
            )
        except (OSError, subprocess.SubprocessError):
            return None
        desktop_id = result.stdout.strip().removesuffix(".desktop")
        if result.returncode != 0 or not desktop_id:
            return None
        return desktop_id if self._applications.contains_id(desktop_id) else None

    def rejection_reason(self, request: str) -> str | None:
        value = self._request_value(request)
        if self._EMAIL.fullmatch(value):
            return (
                "Seu pedido é ambíguo: informe se deseja abrir um cliente de e-mail "
                "instalado ou um webmail específico."
            )
        if self.resolve(request) is not None:
            return None
        if self._SITE_IN_BROWSER.fullmatch(value):
            return (
                "Site não aberto no navegador. Somente destinos HTTP ou HTTPS "
                "válidos e navegadores confiáveis são permitidos."
            )
        if self._FOLDER.fullmatch(value) or self._FILE.fullmatch(value):
            return (
                "Não foi possível abrir o caminho. Ele deve existir dentro da sua pasta "
                "pessoal e estar acessível ao usuário atual."
            )
        if self._SITE.fullmatch(value):
            return "Site não aberto. Somente endereços HTTP ou HTTPS válidos são permitidos."
        if self._UNSAFE_URI.match(value):
            return "Site não aberto. Somente endereços HTTP ou HTTPS válidos são permitidos."
        if self._APPLICATION.fullmatch(value):
            app_match = self._APPLICATION.fullmatch(value)
            assert app_match is not None
            if self._normalize_label(app_match.group(1)) in (
                self._GENERIC_BROWSER | self._DEFAULT_BROWSER
            ):
                return (
                    "Não encontrei um navegador padrão confiável. Você pode dizer "
                    "'abra o Firefox', 'abra o Opera' ou o nome de outro navegador instalado."
                )
            if self._EXPLICIT_NAMED_SITE.match(value):
                return (
                    "Site não identificado com segurança. Informe o domínio HTTPS "
                    "ou use o nome de um site presente no catálogo confiável."
                )
            return (
                "Aplicativo não encontrado entre as entradas confiáveis instaladas. "
                "Verifique o nome ou instale-o pela Central de Aplicativos; "
                "nenhuma instalação foi iniciada automaticamente."
            )
        return None

    def has_desktop_intent(self, request: str) -> bool:
        value = self._request_value(request)
        return any(
            pattern.fullmatch(value) is not None
            for pattern in (
                self._SITE_IN_BROWSER,
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
        normalized = self._normalize_label(value)
        folder = self._STANDARD_FOLDERS.get(normalized)
        if folder is None:
            return None

        xdg_name, fallback_names = folder
        candidates: list[Path] = []
        config = self._home / ".config" / "user-dirs.dirs"

        try:
            lines = config.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []

        prefix = f"XDG_{xdg_name}_DIR="
        for line in lines:
            if not line.startswith(prefix):
                continue
            configured = line.removeprefix(prefix).strip().strip('"')
            configured = configured.replace("$HOME", str(self._home), 1)
            candidates.append(Path(configured).expanduser())
            break

        candidates.extend(self._home / name for name in fallback_names)

        for candidate in candidates:
            try:
                resolved = candidate.resolve(strict=True)
                resolved.relative_to(self._home)
            except (OSError, RuntimeError, ValueError):
                continue
            if resolved.is_dir() and os.access(resolved, os.R_OK | os.X_OK):
                return resolved

        return None

    @staticmethod
    def _normalize_label(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.encode("ascii", "ignore").decode().lower()
        return " ".join(normalized.split())

    @staticmethod
    def _safe_url(raw_value: str) -> str | None:
        value = raw_value.strip().rstrip(".,")
        if not value or any(ord(character) < 32 for character in value):
            return None
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
