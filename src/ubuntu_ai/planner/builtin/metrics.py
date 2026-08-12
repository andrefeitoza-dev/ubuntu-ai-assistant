from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.planner.builtin.registry import BUILTIN_COMMANDS


@dataclass(slots=True)
class BuiltinMetrics:
    """Estatísticas do Builtin Planner."""

    commands: int
    aliases: int


def collect_metrics() -> BuiltinMetrics:
    """Coleta estatísticas do Builtin Planner."""

    return BuiltinMetrics(
        commands=len(BUILTIN_COMMANDS),
        aliases=sum(
            len(command.keywords)
            for command in BUILTIN_COMMANDS
        ),
    )