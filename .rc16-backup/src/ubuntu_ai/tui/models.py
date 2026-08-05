from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class TerminalCommand(StrEnum):
    """Comandos locais reconhecidos pela interface de terminal."""

    HELP = ":help"
    HISTORY = ":history"
    PLUGINS = ":plugins"
    STATUS = ":status"
    QUIT = ":quit"


@dataclass(slots=True, frozen=True)
class TerminalAppConfig:
    """Configuração visual e de consulta da interface de terminal."""

    history_limit: int = 10
    clear_between_tasks: bool = False

    def __post_init__(self) -> None:
        if self.history_limit < 1:
            raise ValueError("history_limit deve ser maior que zero.")
