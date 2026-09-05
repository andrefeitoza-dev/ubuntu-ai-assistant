from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from ubuntu_ai.gui.theme import (
    ACCENT,
    ACCENT_HOVER,
    BACKGROUND,
    BORDER,
    FONT_TINY,
    SUCCESS,
    SURFACE_ALT,
    SURFACE_HOVER,
    TEXT,
)


class CircularVoiceButton(tk.Canvas):
    """Botão circular acessível com dica textual e estados visuais."""

    def __init__(
        self,
        parent: tk.Misc,
        *,
        symbol: str,
        tooltip: str,
        command: Callable[[], None],
        primary: bool = False,
    ) -> None:
        super().__init__(
            parent,
            width=42,
            height=42,
            bg=SURFACE_ALT,
            highlightthickness=1,
            highlightbackground=SURFACE_ALT,
            takefocus=1,
            cursor="hand2",
        )
        self._command = command
        self._symbol = symbol
        self._tooltip_text = tooltip
        self._enabled = True
        self._active = False
        self._base_fill = ACCENT if primary else SURFACE_HOVER
        self._hover_fill = ACCENT_HOVER if primary else BORDER
        self._tooltip_window: tk.Toplevel | None = None
        self._circle = self.create_oval(2, 2, 40, 40, fill=self._base_fill, outline="")
        self._label = self.create_text(21, 21, text=symbol, fill=TEXT, font=FONT_TINY)
        self.bind("<Button-1>", self._activate, add="+")
        self.bind("<Return>", self._activate, add="+")
        self.bind("<space>", self._activate, add="+")
        self.bind("<Enter>", self._enter, add="+")
        self.bind("<Leave>", self._leave, add="+")
        self.bind("<FocusIn>", lambda _event: self.configure(highlightbackground=ACCENT))
        self.bind("<FocusOut>", lambda _event: self.configure(highlightbackground=SURFACE_ALT))

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.configure(cursor="hand2" if enabled else "arrow")
        self.itemconfigure(self._label, text=self._symbol if enabled else "…")

    def set_active(self, active: bool) -> None:
        self._active = active
        self.itemconfigure(self._circle, fill=SUCCESS if active else self._base_fill)

    def _activate(self, _event: tk.Event | None = None) -> str:
        if self._enabled:
            self._command()
        return "break"

    def _enter(self, _event: tk.Event) -> None:
        if not self._active:
            self.itemconfigure(self._circle, fill=self._hover_fill)
        self._show_tooltip()

    def _leave(self, _event: tk.Event) -> None:
        self.itemconfigure(
            self._circle,
            fill=SUCCESS if self._active else self._base_fill,
        )
        self._hide_tooltip()

    def _show_tooltip(self) -> None:
        self._hide_tooltip()
        window = tk.Toplevel(self)
        window.wm_overrideredirect(True)
        window.configure(bg=BORDER)
        window.geometry(f"+{self.winfo_rootx()}+{self.winfo_rooty() - 34}")
        tk.Label(
            window,
            text=self._tooltip_text,
            bg=BACKGROUND,
            fg=TEXT,
            font=FONT_TINY,
            padx=8,
            pady=4,
        ).pack(padx=1, pady=1)
        self._tooltip_window = window

    def _hide_tooltip(self) -> None:
        if self._tooltip_window is not None:
            self._tooltip_window.destroy()
            self._tooltip_window = None
