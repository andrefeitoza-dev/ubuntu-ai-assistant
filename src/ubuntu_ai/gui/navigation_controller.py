from __future__ import annotations

import tkinter as tk


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
        button = getattr(self, "navigation_button", None)
        if button is not None and button.winfo_exists():
            button.configure(text="☰")
        self._hide_capabilities_panel()
        self._hide_automation_panel()
        self._hide_care_panel()
        self._hide_remote_controls()

    def _open_remote_from_menu(self) -> None:
        if not self._remote_controls_visible:
            self._toggle_remote_controls()
        self._watch_navigation_panel(self.remote_controls, self._hide_remote_controls)

    def _open_automation_from_menu(self) -> None:
        self._hide_remote_controls()
        panel = getattr(self, "_automation_panel", None)
        if panel is None or not panel.winfo_ismapped():
            self._show_automation_panel()

    def _open_resources_from_menu(self) -> None:
        self._hide_remote_controls()
        panel = getattr(self, "_resources_panel", None)
        if panel is None or not panel.winfo_ismapped():
            self._show_capabilities()

    def _open_care_from_menu(self) -> None:
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
        panel.place(x=menu_left - 8, y=button_top, width=fitted_width, anchor=tk.NE)

    def _watch_navigation_panel(self, panel: tk.Widget, hide_callback: object) -> None:
        panel.bind(
            "<Leave>",
            lambda _event: self.root.after(
                160,
                self._hide_if_outside_navigation,
                panel,
                hide_callback,
            ),
        )

    def _hide_if_outside_navigation(self, panel: tk.Widget, hide_callback: object) -> None:
        widget = self.root.winfo_containing(
            self.root.winfo_pointerx(), self.root.winfo_pointery()
        )
        while widget is not None:
            if widget is panel or widget is self.navigation_menu:
                return
            widget = getattr(widget, "master", None)
        hide_callback()  # type: ignore[operator]
