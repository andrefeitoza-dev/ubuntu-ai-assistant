"""Respostas locais instantâneas que não precisam de um modelo de linguagem."""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class LocalResponse:
    text: str
    route: str = "local"


class LocalResponder:
    """Resolve consultas simples localmente, sem acionar o Ollama."""

    _WEEKDAYS = (
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    )
    _MONTHS = (
        "janeiro",
        "fevereiro",
        "março",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro",
    )

    _DATE_REQUESTS = {
        "que dia e hoje",
        "qual e o dia de hoje",
        "qual a data de hoje",
        "hoje e que dia",
        "data de hoje",
    }
    _TIME_REQUESTS = {
        "que horas sao",
        "qual e a hora",
        "qual a hora",
        "hora atual",
        "horario atual",
    }
    _HELP_REQUESTS = {
        "help",
        "ajuda",
        "me ajude",
        "o que voce faz",
        "o que posso pedir",
        "como voce pode ajudar",
    }
    _CANCEL_REQUESTS = {
        "cancelar",
        "cancele",
        "cancel",
        "interromper",
    }

    def __init__(
        self,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._now = now or datetime.now

    def respond(self, request: str) -> LocalResponse | None:
        normalized = self._normalize(request)

        if normalized in self._DATE_REQUESTS:
            current = self._now()
            weekday = self._WEEKDAYS[current.weekday()]
            month = self._MONTHS[current.month - 1]
            return LocalResponse(f"Hoje é {weekday}, {current.day} de {month} de {current.year}.")

        if normalized in self._TIME_REQUESTS:
            current = self._now()
            return LocalResponse(f"Agora são {current:%H:%M}.")

        if normalized in self._HELP_REQUESTS:
            return LocalResponse(
                "Posso consultar arquivos, pastas, disco, memória, processos, "
                "rede, serviços, Docker e Git. Também respondo data e hora "
                "instantaneamente. Ações de risco exigem sua confirmação."
            )

        if normalized in self._CANCEL_REQUESTS:
            return LocalResponse("Não há nenhuma operação em andamento para cancelar.")

        return None

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.encode("ascii", "ignore").decode().lower()
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        return " ".join(normalized.split())
