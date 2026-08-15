from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConsoleTheme:
    """Tokens visuais reutilizáveis da interface terminal."""

    success: str = "green"
    warning: str = "yellow"
    error: str = "red"
    info: str = "cyan"
    muted: str = "dim"
    accent: str = "bold cyan"
