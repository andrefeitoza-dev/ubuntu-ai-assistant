from __future__ import annotations

import re
from pathlib import Path

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel


class SafeFileOperationPlanner:
    """Planeja alterações limitadas a nomes simples e pastas pessoais conhecidas."""

    _CREATE = re.compile(
        r"^crie\s+(?:(?:uma?|a)\s+)?pasta\s+(.+?)"
        r"(?:\s+(?:dentro\s+da\s+pasta|dentro\s+de|na\s+pasta|em)\s+(.+))?$",
        re.IGNORECASE,
    )
    _CREATE_FILE = re.compile(
        r"^crie\s+(?:(?:um|o)\s+)?arquivo\s+(.+?)"
        r"(?:\s+(?:dentro\s+da\s+pasta|dentro\s+de|na\s+pasta|em)\s+(.+))?$",
        re.IGNORECASE,
    )
    _REMOVE = re.compile(
        r"^(?:remova|apague|delete)\s+(?:(?:o|a|um|uma)\s+)?"
        r"(?:arquivo|pasta)\s+(.+?)(?:\s+(?:da|do|de|na|no)\s+(.+))?$",
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
    _INTENT = re.compile(
        r"^(?:crie\s+.+(?:pasta|arquivo)|copie|mova|renomeie|envie|remova|apague|delete)\b",
        re.IGNORECASE,
    )
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
        remove = self._REMOVE.fullmatch(value)
        if remove:
            name, folder_label = remove.groups()
            parent = self._folder(folder_label or "inicio")
            if parent is None or not self._safe_name(name):
                return None
            source = parent / name.strip()
            if not source.exists() or source.is_symlink():
                return None
            return self._plan(
                "Mover para a Lixeira",
                f"Move {source} para a Lixeira, permitindo recuperação posterior.",
                ("gio", "trash", str(source)),
            )

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
            return self._creation_plan(
                "Criar pasta",
                f"Cria a pasta {destination} sem sobrescrever conteúdo existente.",
                ("mkdir", str(destination)),
                parent,
            )

        create_file = self._CREATE_FILE.fullmatch(value)
        if create_file:
            name, folder_label = create_file.groups()
            parent = self._folder(folder_label or "inicio")
            if parent is None or not self._safe_name(name):
                return None
            destination = parent / name.strip()
            if destination.exists() or destination.is_symlink():
                return None
            return self._creation_plan(
                "Criar arquivo vazio",
                f"Cria o arquivo vazio {destination} sem sobrescrever conteúdo existente.",
                ("touch", str(destination)),
                parent,
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
        normalized = label.strip().casefold()
        names = self._FOLDERS.get(normalized)
        if names is None:
            custom_name = re.sub(r"^pasta\s+", "", label.strip(), flags=re.IGNORECASE)
            if not self._safe_name(custom_name):
                return None
            candidate = self._home / custom_name
            try:
                resolved = candidate.resolve(strict=True)
                resolved.relative_to(self._home)
            except (OSError, RuntimeError, ValueError):
                return None
            return resolved if resolved.is_dir() and not candidate.is_symlink() else None
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

    @classmethod
    def _creation_plan(
        cls,
        title: str,
        description: str,
        command: tuple[str, ...],
        parent: Path,
    ) -> Plan:
        plan = cls._plan(title, description, command)
        plan.add_step(
            PlanStep(
                title="Atualizar pasta no gerenciador de arquivos",
                description=f"Abre a pasta {parent} para exibir imediatamente o novo item.",
                command=["xdg-open", str(parent)],
            )
        )
        return plan
