from __future__ import annotations

from contextlib import contextmanager
from collections.abc import Iterator

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)


class ProgressRenderer:
    """Cria progresso padronizado para operações longas."""

    def __init__(self, console: Console) -> None:
        self._console = console

    @contextmanager
    def task(self, description: str) -> Iterator[Progress]:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
            console=self._console,
            transient=True,
        )

        with progress:
            progress.add_task(description, total=None)
            yield progress
