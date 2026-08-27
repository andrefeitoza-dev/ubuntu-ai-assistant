from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass

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
class CapabilitiesPanelWidgets:
    """Widgets públicos necessários à coordenação do painel."""

    panel: tk.Frame
    listbox: tk.Listbox
    detail: tk.Label


def build_capabilities_panel(
    root: tk.Misc,
    *,
    on_close: Callable[..., object],
    on_motion: Callable[..., object],
    on_leave: Callable[..., object],
    on_activate: Callable[..., object],
) -> CapabilitiesPanelWidgets:
    """Constrói o painel de recursos sem consultar backend ou executar ações."""

    panel = tk.Frame(
        root,
        bg=BORDER,
        highlightbackground=BORDER,
        highlightthickness=1,
        borderwidth=0,
    )

    surface = tk.Frame(panel, bg=SURFACE_ALT)
    surface.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

    heading = tk.Frame(surface, bg=SURFACE_ALT)
    heading.pack(fill=tk.X, padx=12, pady=(10, 6))

    tk.Label(
        heading,
        text="Recursos e ajuda",
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
        activebackground=SURFACE_HOVER,
        activeforeground=TEXT,
        relief=tk.FLAT,
        borderwidth=0,
        cursor="hand2",
        font=FONT_TINY,
    ).pack(side=tk.RIGHT)

    list_frame = tk.Frame(surface, bg=SURFACE_ALT)
    list_frame.pack(fill=tk.X, padx=12)

    scrollbar = tk.Scrollbar(
        list_frame,
        orient=tk.VERTICAL,
    )
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    listbox = tk.Listbox(
        list_frame,
        height=11,
        bg=SURFACE,
        fg=TEXT,
        selectbackground=ACCENT,
        selectforeground="#101318",
        activestyle="none",
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        font=FONT_SMALL,
        exportselection=False,
        yscrollcommand=scrollbar.set,
    )
    listbox.pack(side=tk.LEFT, fill=tk.X, expand=True)
    scrollbar.configure(command=listbox.yview)

    detail = tk.Label(
        surface,
        text="",
        bg=SURFACE_ALT,
        fg=TEXT,
        justify=tk.LEFT,
        anchor=tk.NW,
        wraplength=440,
        padx=12,
        pady=10,
        font=FONT_TINY,
    )
    detail.pack(fill=tk.X)

    listbox.bind("<Motion>", on_motion)
    listbox.bind("<Leave>", on_leave)
    listbox.bind("<ButtonRelease-1>", on_activate)
    listbox.bind("<Return>", on_activate)

    return CapabilitiesPanelWidgets(
        panel=panel,
        listbox=listbox,
        detail=detail,
    )
