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
        self._keep_navigation_open()
        if not self._remote_controls_visible:
            self._toggle_remote_controls()
        self._watch_navigation_panel(self.remote_controls, self._hide_remote_controls)

    def _open_automation_from_menu(self) -> None:
        self._keep_navigation_open()
        self._hide_remote_controls()
        panel = getattr(self, "_automation_panel", None)
        if panel is None or not panel.winfo_ismapped():
            self._show_automation_panel()

    def _open_resources_from_menu(self) -> None:
        self._keep_navigation_open()
        self._hide_remote_controls()
        panel = getattr(self, "_resources_panel", None)
        if panel is None or not panel.winfo_ismapped():
            self._show_capabilities()

    def _open_care_from_menu(self) -> None:
        self._keep_navigation_open()
        self._hide_remote_controls()
        panel = getattr(self, "_care_panel", None)
        if panel is None or not panel.winfo_ismapped():
            self._show_care_panel()

    def _place_navigation_panel(
        self, panel: tk.Widget, button: tk.Widget, *, width: int
    ) -> None:
        self.root.update_idletasks()
        menu_left = self.navigation_menu.winfo_rootx() - self.root.winfo_rootx()
        button_top = button.winfo_rooty() - self.root.winfo_rooty()
        fitted_width = min(width, max(320, menu_left - 36))
        panel.place(x=menu_left - 3, y=button_top, width=fitted_width, anchor=tk.NE)

    def _schedule_navigation_leave(self, _event: tk.Event | None = None) -> None:
        generation = getattr(self, "_navigation_hover_generation", 0)
        self.root.after(220, self._hide_panels_if_outside_navigation, generation)

    def _keep_navigation_open(self, _event: tk.Event | None = None) -> None:
        self._navigation_hover_generation = (
            getattr(self, "_navigation_hover_generation", 0) + 1
        )

    def _hide_panels_if_outside_navigation(self, generation: int) -> None:
        if generation != getattr(self, "_navigation_hover_generation", 0):
            return
        widget = self.root.winfo_containing(
            self.root.winfo_pointerx(), self.root.winfo_pointery()
        )
        panels = (
            getattr(self, "remote_controls", None),
            getattr(self, "_automation_panel", None),
            getattr(self, "_resources_panel", None),
            getattr(self, "_care_panel", None),
        )
        while widget is not None:
            if widget is self.navigation_menu or widget in panels:
                return
            widget = getattr(widget, "master", None)
        self._hide_capabilities_panel()
        self._hide_automation_panel()
        self._hide_care_panel()
        self._hide_remote_controls()

    def _watch_navigation_panel(self, panel: tk.Widget, hide_callback: object) -> None:
        panel.bind("<Enter>", self._keep_navigation_open, add="+")
        panel.bind(
            "<Leave>",
            lambda _event: self.root.after(
                220,
                self._hide_if_outside_navigation,
                panel,
                hide_callback,
                getattr(self, "_navigation_hover_generation", 0),
            ),
            add="+",
        )

    def _hide_if_outside_navigation(
        self, panel: tk.Widget, hide_callback: object, generation: int
    ) -> None:
        if generation != getattr(self, "_navigation_hover_generation", 0):
            return
        widget = self.root.winfo_containing(
            self.root.winfo_pointerx(), self.root.winfo_pointery()
        )
        while widget is not None:
            if widget is panel or widget is self.navigation_menu:
                return
            widget = getattr(widget, "master", None)
        hide_callback()  # type: ignore[operator]
