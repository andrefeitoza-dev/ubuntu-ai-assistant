from __future__ import annotations

import tkinter as tk
from dataclasses import dataclass

from ubuntu_ai.gui.theme import (
    BACKGROUND,
    CONTENT_PAD,
    FONT_BODY,
    FONT_HERO,
    SURFACE_ALT,
    TEXT,
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
        pady=12,
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
        wraplength=650,
    ).pack(anchor="w")

    return frame
