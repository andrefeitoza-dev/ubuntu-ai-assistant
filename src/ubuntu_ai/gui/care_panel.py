from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass

from ubuntu_ai.gui.theme import (
    BORDER,
    FONT_BODY_BOLD,
    FONT_SMALL,
    FONT_TINY,
    SURFACE_ALT,
    SURFACE_HOVER,
    TEXT,
    TEXT_MUTED,
)


@dataclass(frozen=True, slots=True)
class CareAction:
    title: str
    description: str
    request: str


CARE_ACTIONS = (
    CareAction(
        "Diagnosticar lentidão",
        "Analisa CPU, memória, swap, disco e processos.",
        "Por que meu computador está lento?",
    ),
    CareAction(
        "Liberar espaço",
        "Investiga o uso do disco antes de sugerir alterações.",
        "Analise por que o disco está cheio.",
    ),
    CareAction(
        "Verificar atualizações",
        "Consulta o cache local do APT sem instalar pacotes.",
        "Quais atualizações estão disponíveis?",
    ),
    CareAction(
        "Verificar segurança",
        "Prepara uma auditoria básica sem modificar o sistema.",
        "Faça uma auditoria básica de segurança deste computador.",
    ),
)


@dataclass(frozen=True, slots=True)
class CarePanelWidgets:
    panel: tk.Frame


def build_care_panel(
    parent: tk.Misc,
    *,
    on_close: Callable[[], None],
    on_action: Callable[[str], None],
) -> CarePanelWidgets:
    """Constrói os atalhos de cuidados sem consultar ou alterar o computador."""

    panel = tk.Frame(parent, bg=BORDER, highlightbackground=BORDER, highlightthickness=1)
    surface = tk.Frame(panel, bg=SURFACE_ALT, padx=16, pady=14)
    surface.pack(fill=tk.BOTH, expand=True)

    heading = tk.Frame(surface, bg=SURFACE_ALT)
    heading.pack(fill=tk.X, pady=(0, 10))
    tk.Label(
        heading,
        text="Cuidados do computador",
        bg=SURFACE_ALT,
        fg=TEXT,
        font=FONT_BODY_BOLD,
    ).pack(side=tk.LEFT)
    tk.Button(
        heading,
        text="Fechar",
        command=on_close,
        bg=SURFACE_ALT,
        fg=TEXT_MUTED,
        activebackground=SURFACE_HOVER,
        activeforeground=TEXT,
        relief=tk.FLAT,
        borderwidth=0,
        cursor="hand2",
        font=FONT_TINY,
    ).pack(side=tk.RIGHT)

    for action in CARE_ACTIONS:
        tk.Button(
            surface,
            text=f"{action.title}\n{action.description}",
            command=lambda request=action.request: on_action(request),
            bg=SURFACE_ALT,
            fg=TEXT,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=0,
            anchor="w",
            justify=tk.LEFT,
            cursor="hand2",
            font=FONT_SMALL,
            padx=8,
            pady=8,
        ).pack(fill=tk.X)

    tk.Label(
        surface,
        text="Consultas não alteram o sistema. Ações continuam exigindo confirmação.",
        bg=SURFACE_ALT,
        fg=TEXT_MUTED,
        font=FONT_TINY,
        wraplength=400,
        justify=tk.LEFT,
    ).pack(fill=tk.X, pady=(10, 0))
    return CarePanelWidgets(panel=panel)
