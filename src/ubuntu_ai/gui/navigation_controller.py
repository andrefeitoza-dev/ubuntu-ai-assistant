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
        self.navigation_button.configure(text="☰  ▴")

    def _hide_navigation_menu(self, _event: tk.Event | None = None) -> None:
        menu = getattr(self, "navigation_menu", None)
        if menu is not None and menu.winfo_exists():
            menu.place_forget()
        button = getattr(self, "navigation_button", None)
        if button is not None and button.winfo_exists():
            button.configure(text="☰")

    def _open_remote_from_menu(self) -> None:
        if not self._remote_controls_visible:
            self._toggle_remote_controls()

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
