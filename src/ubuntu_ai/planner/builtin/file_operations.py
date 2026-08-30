from __future__ import annotations

import re
from pathlib import Path

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel


class SafeFileOperationPlanner:
    """Planeja alterações limitadas a nomes simples e pastas pessoais conhecidas."""

    _CREATE = re.compile(
        r"^crie\s+(?:(?:uma?|a)\s+)?pasta\s+(.+?)(?:\s+em\s+(.+))?$",
        re.IGNORECASE,
    )
    _TRANSFER = re.compile(
        r"^(copie|mova)\s+(?:o\s+)?arquivo\s+(.+?)\s+de\s+(.+?)\s+para\s+(.+)$",
        re.IGNORECASE,
    )
    _RENAME = re.compile(
        r"^renomeie\s+(?:o\s+arquivo|a\s+pasta)\s+(.+?)\s+para\s+(.+)$",
        re.IGNORECASE,
    )
    _TRASH = re.compile(
        r"^(?:envie|mova)\s+(?:o\s+arquivo|a\s+pasta)\s+(.+?)\s+"
        r"(?:para\s+a\s+lixeira|à\s+lixeira)$",
        re.IGNORECASE,
    )
    _INTENT = re.compile(r"^(?:crie\s+.+pasta|copie|mova|renomeie|envie)\b", re.IGNORECASE)
    _FOLDERS = {
        "inicio": (),
        "home": (),
        "documentos": ("Documentos", "Documents"),
        "documents": ("Documents", "Documentos"),
        "downloads": ("Downloads",),
        "imagens": ("Imagens", "Pictures"),
        "pictures": ("Pictures", "Imagens"),
    }
    _FORBIDDEN = frozenset("/\\;&|`\n\r\x00*?[]{}")

    def __init__(self, home: Path | None = None) -> None:
        self._home = (home or Path.home()).expanduser().resolve()

    def try_create_plan(self, request: str) -> Plan | None:
        value = request.strip().rstrip(".!?").strip()
        trash = self._TRASH.fullmatch(value)
        if trash:
            name = trash.group(1)
            if not self._safe_name(name):
                return None
            source = self._home / name.strip()
            if not source.exists() or source.is_symlink():
                return None
            return self._plan(
                "Mover para a Lixeira",
                f"Move {source} para a Lixeira, permitindo recuperação posterior.",
                ("gio", "trash", str(source)),
            )

        create = self._CREATE.fullmatch(value)
        if create:
            name, folder_label = create.groups()
            parent = self._folder(folder_label or "inicio")
            if parent is None or not self._safe_name(name):
                return None
            destination = parent / name.strip()
            if destination.exists() or destination.is_symlink():
                return None
            return self._plan(
                "Criar pasta",
                f"Cria a pasta {destination} sem sobrescrever conteúdo existente.",
                ("mkdir", str(destination)),
            )

        transfer = self._TRANSFER.fullmatch(value)
        if transfer:
            operation, name, source_label, destination_label = transfer.groups()
            source_dir = self._folder(source_label)
            destination_dir = self._folder(destination_label)
            if source_dir is None or destination_dir is None or not self._safe_name(name):
                return None
            source = source_dir / name.strip()
            destination = destination_dir / name.strip()
            if not source.is_file() or source.is_symlink() or destination.exists():
                return None
            executable = "cp" if operation.casefold() == "copie" else "mv"
            title = "Copiar arquivo" if executable == "cp" else "Mover arquivo"
            return self._plan(
                title,
                f"{title} de {source} para {destination}, sem sobrescrever o destino.",
                (executable, str(source), str(destination)),
            )

        rename = self._RENAME.fullmatch(value)
        if rename:
            old_name, new_name = rename.groups()
            if not self._safe_name(old_name) or not self._safe_name(new_name):
                return None
            source = self._home / old_name.strip()
            destination = self._home / new_name.strip()
            if not source.exists() or source.is_symlink() or destination.exists():
                return None
            return self._plan(
                "Renomear item",
                f"Renomeia {source} para {destination}, sem sobrescrever o destino.",
                ("mv", str(source), str(destination)),
            )
        return None

    @classmethod
    def has_file_operation_intent(cls, request: str) -> bool:
        return cls._INTENT.match(request.strip()) is not None

    def rejection_reason(self, request: str) -> str | None:
        if not self.has_file_operation_intent(request) or self.try_create_plan(request):
            return None
        return (
            "Alteração não planejada. Use nomes simples e pastas pessoais conhecidas; "
            "a origem deve existir e o destino não pode existir nem ser um link simbólico."
        )

    def _folder(self, label: str) -> Path | None:
        names = self._FOLDERS.get(label.strip().casefold())
        if names is None:
            return None
        if not names:
            return self._home
        return next((self._home / name for name in names if (self._home / name).is_dir()), None)

    @classmethod
    def _safe_name(cls, value: str) -> bool:
        name = value.strip()
        return bool(name) and name not in {".", ".."} and not any(c in name for c in cls._FORBIDDEN)

    @staticmethod
    def _plan(title: str, description: str, command: tuple[str, ...]) -> Plan:
        plan = Plan(goal=title, estimated_seconds=2, risk=RiskLevel.HIGH, planner="builtin")
        plan.add_step(PlanStep(title=title, description=description, command=list(command)))
        return plan
