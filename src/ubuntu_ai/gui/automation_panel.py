from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass

from ubuntu_ai.autonomy.long_tasks import LongTask
from ubuntu_ai.autonomy.observability import AutomationMetrics
from ubuntu_ai.gui.theme import (
    ACCENT,
    BORDER,
    FONT_SMALL,
    FONT_SMALL_BOLD,
    FONT_TINY,
    SURFACE,
    SURFACE_ALT,
    SURFACE_HOVER,
    TEXT,
    TEXT_MUTED,
)


@dataclass(frozen=True, slots=True)
class AutomationPanelWidgets:
    """Widgets utilizados pela coordenação do painel de automação."""

    panel: tk.Frame
    tasks: tk.Listbox
    summary: tk.Label


def task_row(task: LongTask) -> str:
    """Formata uma tarefa longa para exibição na lista."""

    progress = round(task.progress * 100)
    return f"{task.task_id} · {task.status.value} · {progress}% · {task.description}"


def summary_text(
    *,
    target: str,
    metrics: AutomationMetrics,
    event_count: int,
) -> str:
    """Formata o resumo operacional e auditável do painel."""

    return (
        f"Destino: {target} · "
        f"Ativas: {metrics.active_tasks} · "
        f"Concluídas: {metrics.completed_tasks} · "
        f"Falhas: {metrics.failed_tasks} · "
        f"Eventos auditáveis: {event_count}"
    )


def build_automation_panel(
    root: tk.Misc,
    *,
    on_close: Callable[..., object],
    on_action: Callable[[str], object],
) -> AutomationPanelWidgets:
    """Constrói o painel sem consultar backend ou controlar tarefas."""

    panel = tk.Frame(
        root,
        bg=BORDER,
        highlightthickness=1,
    )
    surface = tk.Frame(panel, bg=SURFACE_ALT)
    surface.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

    heading = tk.Frame(surface, bg=SURFACE_ALT)
    heading.pack(fill=tk.X, padx=12, pady=(10, 6))

    tk.Label(
        heading,
        text="Agentes, tarefas e auditoria",
        bg=SURFACE_ALT,
        fg=TEXT,
        font=FONT_SMALL_BOLD,
    ).pack(side=tk.LEFT)

    tk.Button(
        heading,
        text="Fechar",
        command=on_close,
        bg=SURFACE_ALT,
        fg=TEXT_MUTED,
        relief=tk.FLAT,
        font=FONT_TINY,
    ).pack(side=tk.RIGHT)

    summary = tk.Label(
        surface,
        text="",
        bg=SURFACE_ALT,
        fg=TEXT,
        justify=tk.LEFT,
        anchor=tk.W,
        font=FONT_TINY,
    )
    summary.pack(fill=tk.X, padx=12, pady=(0, 8))

    tasks = tk.Listbox(
        surface,
        height=8,
        bg=SURFACE,
        fg=TEXT,
        selectbackground=ACCENT,
        selectforeground="#101318",
        activestyle="none",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        exportselection=False,
        font=FONT_SMALL,
    )
    tasks.pack(fill=tk.X, padx=12)

    controls = tk.Frame(surface, bg=SURFACE_ALT)
    controls.pack(fill=tk.X, padx=12, pady=10)

    for label, action in (
        ("Atualizar", "refresh"),
        ("Pausar", "pause"),
        ("Retomar", "resume"),
        ("Cancelar", "cancel"),
    ):
        tk.Button(
            controls,
            text=label,
            command=lambda selected=action: on_action(selected),
            bg=SURFACE,
            fg=TEXT,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT,
            relief=tk.FLAT,
            font=FONT_TINY,
            padx=9,
            pady=5,
        ).pack(side=tk.LEFT, padx=(0, 6))

    tk.Label(
        surface,
        text=("Dica: use “agentes: diagnóstico completo” para criar uma prévia segura."),
        bg=SURFACE_ALT,
        fg=TEXT_MUTED,
        font=FONT_TINY,
    ).pack(fill=tk.X, padx=12, pady=(0, 10))

    return AutomationPanelWidgets(
        panel=panel,
        tasks=tasks,
        summary=summary,
    )
