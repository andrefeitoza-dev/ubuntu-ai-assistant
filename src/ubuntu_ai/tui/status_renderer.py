from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

from ubuntu_ai.tui.theme import ConsoleTheme


class StatusRenderer:
    """Renderiza mensagens de status consistentes."""

    def __init__(
        self,
        console: Console,
        theme: ConsoleTheme | None = None,
    ) -> None:
        self._console = console
        self._theme = theme or ConsoleTheme()

    def success(self, message: str) -> None:
        self._console.print(
            Panel.fit(
                f"[{self._theme.success}]✓ {message}[/{self._theme.success}]",
                title="Concluído",
            )
        )

    def warning(self, message: str) -> None:
        self._console.print(f"[{self._theme.warning}]! {message}[/{self._theme.warning}]")

    def error(self, message: str) -> None:
        self._console.print(
            Panel.fit(
                f"[{self._theme.error}]✗ {message}[/{self._theme.error}]",
                title="Erro",
            )
        )

    def info(self, message: str) -> None:
        self._console.print(f"[{self._theme.info}]• {message}[/{self._theme.info}]")
