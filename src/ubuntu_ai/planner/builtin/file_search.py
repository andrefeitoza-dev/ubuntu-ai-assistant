from __future__ import annotations

import glob
import re
from dataclasses import dataclass
from pathlib import Path

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel


@dataclass(frozen=True, slots=True)
class FileSearchRequest:
    term: str
    item_type: str | None = None


class SafeFileSearchPlanner:
    """Cria buscas locais somente leitura sem executar uma linha de shell."""

    _REQUEST = re.compile(
        r"^(?:encontre|localize|procure|busque|ache|onde\s+(?:est[aá]|fica))\s+"
        r"(?:(?:o|a|um|uma)\s+)?"
        r"(?:(arquivos?|pastas?|diret[oó]rios?)\s+)?(.+?)"
        r"(?:\s+(?:no|neste|nesse)\s+(?:computador|sistema))?$",
        re.IGNORECASE,
    )
    _FORBIDDEN = frozenset(";&|`\n\r\x00")
    _MAX_TERM_LENGTH = 120
    _SEARCH_INTENT = re.compile(
        r"^(?:encontre|localize|procure|busque|ache|onde\s+(?:est[aá]|fica))\b",
        re.IGNORECASE,
    )

    def __init__(self, home: Path | None = None, max_depth: int = 6) -> None:
        if max_depth < 1:
            raise ValueError("A profundidade da busca deve ser maior que zero.")
        self._home = (home or Path.home()).expanduser()
        self._max_depth = max_depth

    def try_create_plan(self, request: str) -> Plan | None:
        parsed = self.parse(request)
        if parsed is None:
            return None

        command = [
            "find",
            str(self._home),
            "-maxdepth",
            str(self._max_depth),
        ]
        if parsed.item_type is not None:
            command.extend(("-type", parsed.item_type))
        command.extend(("-iname", f"*{glob.escape(parsed.term)}*", "-print"))

        label = "arquivo ou pasta"
        if parsed.item_type == "f":
            label = "arquivo"
        elif parsed.item_type == "d":
            label = "pasta"

        plan = Plan(
            goal=f"Localizar {label}: {parsed.term}",
            estimated_seconds=3,
            risk=RiskLevel.LOW,
            planner="builtin",
        )
        plan.add_step(
            PlanStep(
                title=f"Localizar {label}",
                description=("Pesquisa no diretório pessoal com as permissões do usuário atual."),
                command=command,
            )
        )
        return plan

    @classmethod
    def has_search_intent(cls, request: str) -> bool:
        return cls._SEARCH_INTENT.match(request.strip()) is not None

    @classmethod
    def rejection_reason(cls, request: str) -> str | None:
        if not cls.has_search_intent(request) or cls.parse(request) is not None:
            return None
        return (
            "Busca não executada. Informe somente o nome do arquivo ou da pasta, "
            "sem caminhos, operadores de shell ou referências como '..'."
        )

    @classmethod
    def parse(cls, request: str) -> FileSearchRequest | None:
        match = cls._REQUEST.fullmatch(request.strip())
        if match is None:
            return None

        kind, raw_term = match.groups()
        term = raw_term.strip().strip("\"'").rstrip("?.!").strip()
        term = re.sub(
            r"^(?:chamad[oa]s?|com\s+(?:o\s+)?nome)\s+",
            "",
            term,
            flags=re.IGNORECASE,
        ).strip()
        if term.casefold() in {"pdf", "pdfs"}:
            term = ".pdf"
        if not term or len(term) > cls._MAX_TERM_LENGTH:
            return None
        if term.casefold() in {"arquivo", "pasta", "diretório", "diretorio"}:
            return None
        if term in {".", ".."} or "/" in term or "\\" in term:
            return None
        if any(character in term for character in cls._FORBIDDEN):
            return None

        item_type = None
        if kind and kind.casefold().startswith("arquivo"):
            item_type = "f"
        elif kind:
            item_type = "d"
        return FileSearchRequest(term=term, item_type=item_type)
