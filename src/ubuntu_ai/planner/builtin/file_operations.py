from __future__ import annotations

import os
import re
from difflib import get_close_matches
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
        r"^(?:remova|apague|delete|exclua)\s+(?:(?:o|a|um|uma)\s+)?"
        r"(arquivo|pasta)\s+(.+?)(?:\s+(?:dentro\s+da\s+pasta|dentro\s+de|"
        r"da\s+pasta|na\s+pasta|da|do|de|na|no)\s+(.+))?$",
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
        r"^(?:crie\s+.+(?:pasta|arquivo)|copie|mova|renomeie|envie|remova|apague|delete|exclua)\b",
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
            item_kind, name, folder_label = remove.groups()
            source = self._removal_source(item_kind, name, folder_label)
            if source is None:
                return None
            parent = source.parent
            return self._trash_plan(
                "Mover para a Lixeira",
                f"Origem: {source}. Move o item para a Lixeira, permitindo recuperação posterior.",
                ("gio", "trash", str(source)),
                parent,
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
        value = request.strip().rstrip(".!?").strip()
        remove = self._REMOVE.fullmatch(value)
        if remove:
            item_kind, name, folder_label = remove.groups()
            if self._safe_name(name):
                matches = self._matching_items(item_kind, name.strip())
                if folder_label is None and len(matches) > 1:
                    paths = "\n".join(f"• {path}" for path in matches[:5])
                    return (
                        "Encontrei mais de um item com esse nome. Informe a pasta de origem "
                        f"para escolher com segurança:\n{paths}"
                    )
                location = "na sua pasta pessoal"
                if folder_label is not None:
                    parent = self._folder(folder_label)
                    location = (
                        f"em {parent}" if parent is not None else f'na pasta "{folder_label}"'
                    )
                message = (
                    f'Não encontrei {self._item_article(item_kind)} {item_kind} "{name.strip()}" '
                    f"{location}. Nada foi excluído. Verifique o nome ou informe a pasta de origem."
                )
                suggestions = self._similar_items(item_kind, name.strip(), folder_label)
                if suggestions:
                    paths = "\n".join(f"• {path}" for path in suggestions)
                    message += f"\nItens com nomes parecidos:\n{paths}"
                return message
        return (
            "Alteração não planejada. Use nomes simples e pastas pessoais conhecidas; "
            "a origem deve existir e o destino não pode existir nem ser um link simbólico."
        )

    def _removal_source(self, item_kind: str, name: str, folder_label: str | None) -> Path | None:
        if not self._safe_name(name):
            return None
        if folder_label is not None:
            parent = self._folder(folder_label)
            candidate = parent / name.strip() if parent is not None else None
            if candidate is not None and self._matches_kind(candidate, item_kind):
                return candidate
            return None

        direct = self._home / name.strip()
        if self._matches_kind(direct, item_kind):
            return direct
        matches = self._matching_items(item_kind, name.strip())
        return matches[0] if len(matches) == 1 else None

    def _matching_items(self, item_kind: str, name: str) -> list[Path]:
        matches: list[Path] = []
        for root, directories, files in os.walk(self._home, followlinks=False):
            directories[:] = [
                entry
                for entry in directories
                if not entry.startswith(".") and not (Path(root) / entry).is_symlink()
            ]
            entries = files if item_kind.casefold() == "arquivo" else directories
            if name in entries:
                candidate = Path(root) / name
                if self._matches_kind(candidate, item_kind):
                    matches.append(candidate)
                    if len(matches) > 5:
                        break
        return matches

    def _similar_items(
        self, item_kind: str, name: str, folder_label: str | None
    ) -> list[Path]:
        if folder_label is not None:
            parent = self._folder(folder_label)
            candidates = self._items_in(parent, item_kind) if parent is not None else []
        else:
            candidates = []
            for root, directories, files in os.walk(self._home, followlinks=False):
                directories[:] = [
                    entry
                    for entry in directories
                    if not entry.startswith(".") and not (Path(root) / entry).is_symlink()
                ]
                entries = files if item_kind.casefold() == "arquivo" else directories
                candidates.extend(Path(root) / entry for entry in entries)

        by_name: dict[str, list[Path]] = {}
        for candidate in candidates:
            if self._matches_kind(candidate, item_kind):
                by_name.setdefault(candidate.name, []).append(candidate)
        similar_names = get_close_matches(name, by_name, n=3, cutoff=0.6)
        return [path for similar_name in similar_names for path in by_name[similar_name]][:3]

    @classmethod
    def _items_in(cls, parent: Path, item_kind: str) -> list[Path]:
        try:
            entries = list(parent.iterdir())
        except OSError:
            return []
        return [entry for entry in entries if cls._matches_kind(entry, item_kind)]

    @staticmethod
    def _item_article(item_kind: str) -> str:
        return "o" if item_kind.casefold() == "arquivo" else "a"

    @staticmethod
    def _matches_kind(path: Path, item_kind: str) -> bool:
        if path.is_symlink():
            return False
        return path.is_file() if item_kind.casefold() == "arquivo" else path.is_dir()

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

    @classmethod
    def _trash_plan(
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
                description=f"Abre a pasta {parent} para atualizar a visualização após a exclusão.",
                command=["xdg-open", str(parent)],
            )
        )
        return plan
