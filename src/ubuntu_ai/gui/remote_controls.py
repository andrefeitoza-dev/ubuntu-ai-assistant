from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass

from ubuntu_ai.gui.theme import (
    BACKGROUND,
    FONT_TINY,
    SURFACE_ALT,
    SURFACE_HOVER,
    TEXT,
    TEXT_MUTED,
)


@dataclass(frozen=True, slots=True)
class RemoteControlsWidgets:
    """Widgets necessários à coordenação de destinos locais e remotos."""

    button: tk.Button
    container: tk.Frame
    target_variable: tk.StringVar
    target_menu: tk.OptionMenu


def remote_button_text(target: str, *, expanded: bool) -> str:
    """Mantém o destino selecionado sempre visível no botão."""

    indicator = "▴" if expanded else "▾"
    return f"Computador: {target}  {indicator}"


def place_remote_controls(
    container: tk.Frame,
    button: tk.Button,
    root: tk.Misc,
) -> None:
    """Exibe as opções abaixo da aba, sem comprimir ou esconder o cabeçalho."""

    root.update_idletasks()
    button_right = button.winfo_rootx() - root.winfo_rootx() + button.winfo_width()
    button_bottom = button.winfo_rooty() - root.winfo_rooty() + button.winfo_height()
    container.place(x=button_right, y=button_bottom + 6, width=500, anchor=tk.NE)
    container.lift()


def build_remote_controls(
    header: tk.Misc,
    *,
    panel_parent: tk.Misc | None = None,
    on_toggle: Callable[[], object],
    on_target_selected: Callable[[str], object],
    on_add: Callable[[], object],
    on_remove: Callable[[], object],
    on_diagnose: Callable[[], object],
) -> RemoteControlsWidgets:
    """Constrói controles sem selecionar destinos ou executar SSH."""

    button = tk.Button(
        header,
        text=remote_button_text("local", expanded=False),
        command=on_toggle,
        bg=SURFACE_ALT,
        fg=TEXT,
        activebackground=SURFACE_HOVER,
        activeforeground=TEXT,
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        takefocus=True,
        font=FONT_TINY,
        padx=9,
        pady=4,
    )
    button.pack(side=tk.RIGHT, padx=(0, 16))

    container = tk.Frame(
        panel_parent or header,
        bg=BACKGROUND,
        padx=14,
        pady=12,
        highlightbackground=SURFACE_HOVER,
        highlightthickness=1,
    )

    tk.Label(
        container,
        text="Destino:",
        bg=BACKGROUND,
        fg=TEXT_MUTED,
        font=FONT_TINY,
    ).pack(side=tk.LEFT, padx=(0, 6))

    target_variable = tk.StringVar(value="local")
    target_menu = tk.OptionMenu(
        container,
        target_variable,
        "local",
        command=on_target_selected,
    )
    target_menu.configure(
        bg=SURFACE_ALT,
        fg=TEXT,
        activebackground=SURFACE_HOVER,
        activeforeground=TEXT,
        highlightthickness=0,
        borderwidth=0,
        font=FONT_TINY,
        cursor="hand2",
    )
    target_menu["menu"].configure(
        bg=SURFACE_ALT,
        fg=TEXT,
    )
    target_menu.pack(side=tk.LEFT)

    for label, command in (
        ("+", on_add),
        ("−", on_remove),
        ("Diagnosticar", on_diagnose),
    ):
        tk.Button(
            container,
            text=label,
            command=command,
            bg=BACKGROUND,
            fg=TEXT_MUTED,
            activebackground=SURFACE_HOVER,
            activeforeground=TEXT,
            relief=tk.FLAT,
            borderwidth=0,
            cursor="hand2",
            takefocus=True,
            font=FONT_TINY,
        ).pack(side=tk.LEFT, padx=(5, 0))

    return RemoteControlsWidgets(
        button=button,
        container=container,
        target_variable=target_variable,
        target_menu=target_menu,
    )
