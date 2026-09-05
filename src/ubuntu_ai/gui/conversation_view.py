from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass

from ubuntu_ai.gui.theme import (
    ACCENT,
    BACKGROUND,
    CONTENT_PAD,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_HERO,
    SURFACE_ALT,
    TEXT,
    TEXT_MUTED,
)


@dataclass(frozen=True, slots=True)
class WelcomeWidgets:
    frame: tk.Frame
    icon: tk.PhotoImage | None


def build_welcome(
    parent: tk.Misc,
    *,
    window_icon: tk.PhotoImage | None,
) -> WelcomeWidgets:
    frame = tk.Frame(
        parent,
        bg=BACKGROUND,
    )
    frame.pack(
        fill=tk.X,
        pady=(55, 24),
    )

    icon: tk.PhotoImage | None = None
    if window_icon is not None:
        icon = window_icon.subsample(4, 4)
        tk.Label(
            frame,
            image=icon,
            bg=BACKGROUND,
            borderwidth=0,
        ).pack(pady=(0, 20))

    tk.Label(
        frame,
        text="Como posso ajudar?",
        bg=BACKGROUND,
        fg=TEXT,
        font=FONT_HERO,
    ).pack()

    return WelcomeWidgets(frame=frame, icon=icon)


def add_setup_prompt(
    parent: tk.Misc,
    *,
    ollama_available: bool,
    model: str,
    on_configure: Callable[[], None],
) -> tk.Frame:
    frame = tk.Frame(parent, bg=SURFACE_ALT, padx=18, pady=14)
    frame.pack(fill=tk.X, padx=CONTENT_PAD, pady=(24, 0))
    title = "Finalize a configuração da IA local"
    detail = (
        f"O modelo {model} ainda precisa ser preparado."
        if ollama_available
        else "O Ollama ainda não foi encontrado neste computador."
    )
    tk.Label(
        frame,
        text=title,
        bg=SURFACE_ALT,
        fg=TEXT,
        font=FONT_BODY_BOLD,
    ).pack(anchor="w")
    tk.Label(
        frame,
        text=detail + " As respostas locais continuam disponíveis.",
        bg=SURFACE_ALT,
        fg=TEXT_MUTED,
        font=FONT_BODY,
        justify=tk.LEFT,
        wraplength=560,
    ).pack(anchor="w", pady=(6, 12))
    tk.Button(
        frame,
        text="Configurar IA local",
        command=on_configure,
        bg=ACCENT,
        fg="#101318",
        relief=tk.FLAT,
        borderwidth=0,
        padx=14,
        pady=8,
        cursor="hand2",
        font=FONT_BODY_BOLD,
    ).pack(anchor="w")
    return frame


def add_user_message(
    parent: tk.Misc,
    *,
    message: str,
) -> tk.Frame:
    frame = tk.Frame(
        parent,
        bg=BACKGROUND,
    )
    frame.pack(
        fill=tk.X,
        pady=10,
        padx=CONTENT_PAD,
    )

    bubble = tk.Label(
        frame,
        text=message,
        bg=SURFACE_ALT,
        fg=TEXT,
        font=FONT_BODY,
        justify=tk.LEFT,
        wraplength=560,
        padx=17,
        pady=14,
    )
    bubble.pack(side=tk.RIGHT)
    return frame


def add_system_message(
    parent: tk.Misc,
    *,
    message: str,
    color: str = TEXT,
) -> tk.Frame:
    frame = tk.Frame(
        parent,
        bg=BACKGROUND,
    )
    frame.pack(
        fill=tk.X,
        padx=CONTENT_PAD,
        pady=12,
    )

    tk.Label(
        frame,
        text=message,
        bg=BACKGROUND,
        fg=color,
        font=FONT_BODY,
        justify=tk.LEFT,
        wraplength=720,
        padx=2,
        pady=4,
    ).pack(anchor="w")

    return frame
