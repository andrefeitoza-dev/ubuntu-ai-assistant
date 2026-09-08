from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from ubuntu_ai.gui.theme import BACKGROUND, SURFACE_HOVER, TEXT, TEXT_MUTED


class HeaderMenuButton(tk.Canvas):
    """Botão vetorial de menu com três linhas, independente de glifos da fonte."""

    def __init__(self, parent: tk.Misc, *, command: Callable[[], None]) -> None:
        super().__init__(
            parent,
            width=38,
            height=32,
            bg=BACKGROUND,
            highlightthickness=0,
            borderwidth=0,
            cursor="hand2",
            takefocus=1,
        )
        self._command = command
        self._lines = tuple(
            self.create_line(10, y, 28, y, fill=TEXT_MUTED, width=2)
            for y in (10, 16, 22)
        )
        self.bind("<Button-1>", self._activate)
        self.bind("<Return>", self._activate)
        self.bind("<space>", self._activate)
        self.bind("<Enter>", lambda _event: self._set_visual(True))
        self.bind("<Leave>", lambda _event: self._set_visual(False))
        self.bind("<FocusIn>", lambda _event: self._set_visual(True))
        self.bind("<FocusOut>", lambda _event: self._set_visual(False))

    def _activate(self, _event: tk.Event | None = None) -> str:
        self.focus_set()
        self._command()
        return "break"

    def _set_visual(self, active: bool) -> None:
        self.configure(bg=SURFACE_HOVER if active else BACKGROUND)
        color = TEXT if active else TEXT_MUTED
        for line in self._lines:
            self.itemconfigure(line, fill=color)


class NavigationControllerMixin:
    """Coordena o menu único do cabeçalho e seus painéis existentes."""

    def _toggle_navigation_menu(self) -> None:
        if self.navigation_menu.winfo_ismapped():
            self._hide_navigation_menu()
            return
        self.root.update_idletasks()
        button_right = (
            self.navigation_button.winfo_rootx()
            - self.root.winfo_rootx()
            + self.navigation_button.winfo_width()
        )
        button_bottom = (
            self.navigation_button.winfo_rooty()
            - self.root.winfo_rooty()
            + self.navigation_button.winfo_height()
        )
        self.navigation_menu.place(x=button_right, y=button_bottom + 6, width=245, anchor=tk.NE)
        self.navigation_menu.lift()

    def _hide_navigation_menu(self, _event: tk.Event | None = None) -> None:
        menu = getattr(self, "navigation_menu", None)
        if menu is not None and menu.winfo_exists():
            menu.place_forget()
        self._hide_capabilities_panel()
        self._hide_automation_panel()
        self._hide_care_panel()
        self._hide_remote_controls()

    def _open_remote_from_menu(self) -> None:
        if not self._remote_controls_visible:
            self._toggle_remote_controls()
        self._watch_navigation_panel(self.remote_controls, self._hide_remote_controls)
        self._raise_navigation_menu()

    def _open_automation_from_menu(self) -> None:
        self._hide_remote_controls()
        panel = getattr(self, "_automation_panel", None)
        if panel is None or not panel.winfo_ismapped():
            self._show_automation_panel()
        self._raise_navigation_menu()

    def _open_resources_from_menu(self) -> None:
        self._hide_remote_controls()
        panel = getattr(self, "_resources_panel", None)
        if panel is None or not panel.winfo_ismapped():
            self._show_capabilities()
        self._raise_navigation_menu()

    def _open_care_from_menu(self) -> None:
        self._hide_remote_controls()
        panel = getattr(self, "_care_panel", None)
        if panel is None or not panel.winfo_ismapped():
            self._show_care_panel()
        self._raise_navigation_menu()

    def _raise_navigation_menu(self) -> None:
        """Mantém a lista de tópicos acima dos painéis laterais irmãos."""
        if self.navigation_menu.winfo_ismapped():
            self.navigation_menu.lift()

    def _place_navigation_panel(
        self, panel: tk.Widget, button: tk.Widget, *, width: int
    ) -> None:
        self.root.update_idletasks()
        menu_left = self.navigation_menu.winfo_rootx() - self.root.winfo_rootx()
        button_top = button.winfo_rooty() - self.root.winfo_rooty()
        fitted_width = min(width, max(320, menu_left - 36))
        panel.place(x=menu_left - 3, y=button_top, width=fitted_width, anchor=tk.NE)

    def _watch_navigation_panel(self, panel: tk.Widget, hide_callback: object) -> None:
        # O painel permanece aberto durante a navegação. O fechamento acontece
        # pelo botão do menu, pela tecla Esc ou por um clique fora da navegação.
        panel.lift()
