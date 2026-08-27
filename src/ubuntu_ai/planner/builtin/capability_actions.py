from __future__ import annotations

import unicodedata
from pathlib import Path

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel


class CapabilityActionPlanner:
    """Planos determinísticos de consulta anunciados no catálogo."""

    def __init__(self, home: Path | None = None) -> None:
        self._home = (home or Path.home()).expanduser()

    def try_create_plan(self, phrase: str) -> Plan | None:
        normalized = self._normalize(phrase)

        words = set(normalized.split())

        if (
            words & {"pdf", "pdfs"}
            and words & {"documentos", "documents"}
            and words & {"localize", "encontre", "procure", "busque", "mostre"}
        ):
            documents = self._documents_directory()
            return self._plan(
                goal="Localizar arquivos PDF em Documentos",
                title="Arquivos PDF em Documentos",
                description=("Pesquisa somente arquivos PDF dentro da pasta Documentos."),
                command=(
                    "find",
                    str(documents),
                    "-maxdepth",
                    "6",
                    "-type",
                    "f",
                    "-iname",
                    "*.pdf",
                    "-print",
                ),
                estimated_seconds=3,
            )

        if (
            words & {"pasta", "pastas", "diretorio", "diretorios"}
            and "espaco" in words
            and words & {"mais", "maior", "ocupa", "ocupam", "uso"}
        ):
            return self._plan(
                goal="Comparar o espaço das pastas pessoais",
                title="Uso das pastas pessoais",
                description=("Calcula o espaço utilizado no primeiro nível da pasta pessoal."),
                command=(
                    "du",
                    "-x",
                    "-h",
                    "--max-depth=1",
                    str(self._home),
                ),
                estimated_seconds=8,
            )

        if (
            words & {"processo", "processos"}
            and "memoria" in words
            and words & {"mais", "maior", "usam", "uso", "consumo"}
        ):
            return self._plan(
                goal="Mostrar processos por uso de memória",
                title="Processos por memória",
                description=("Lista processos ordenados do maior para o menor uso de memória."),
                command=(
                    "ps",
                    "-eo",
                    "pid,comm,%mem,%cpu",
                    "--sort=-%mem",
                ),
            )

        if "docker" in words and words & {"log", "logs", "registro", "registros", "journal"}:
            return self._plan(
                goal="Consultar logs do serviço Docker",
                title="Logs do serviço Docker",
                description=("Consulta as últimas entradas do journal sem alterar o serviço."),
                command=(
                    "journalctl",
                    "--no-pager",
                    "-u",
                    "docker.service",
                    "-n",
                    "100",
                ),
                estimated_seconds=2,
            )

        return None

    def _documents_directory(self) -> Path:
        candidates = (
            self._home / "Documents",
            self._home / "Documentos",
        )
        return next(
            (candidate for candidate in candidates if candidate.is_dir()),
            candidates[0],
        )

    @staticmethod
    def _plan(
        *,
        goal: str,
        title: str,
        description: str,
        command: tuple[str, ...],
        estimated_seconds: int = 1,
    ) -> Plan:
        plan = Plan(
            goal=goal,
            estimated_seconds=estimated_seconds,
            risk=RiskLevel.LOW,
            planner="builtin",
        )
        plan.add_step(
            PlanStep(
                title=title,
                description=description,
                command=list(command),
            )
        )
        return plan

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.strip().lower())
        ascii_text = "".join(
            character for character in normalized if not unicodedata.combining(character)
        )
        return " ".join(ascii_text.rstrip("?.!").split())
