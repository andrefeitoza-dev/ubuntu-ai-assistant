from __future__ import annotations

import tkinter as tk

from ubuntu_ai.gui.care_panel import build_care_panel


class PanelControllerMixin:
    """Coordena o painel de cuidados e o fechamento de painéis flutuantes."""

    def _show_care_panel(self) -> None:
        self._hide_capabilities_panel()
        self._hide_automation_panel()
        panel = getattr(self, "_care_panel", None)
        if panel is not None and panel.winfo_ismapped():
            self._hide_care_panel()
            return
        if panel is None or not panel.winfo_exists():
            widgets = build_care_panel(
                self.root,
                on_close=self._hide_care_panel,
                on_action=self._start_care_action,
            )
            panel = widgets.panel
            self._care_panel = panel
        self.root.update_idletasks()
        button_right = (
            self.care_button.winfo_rootx()
            - self.root.winfo_rootx()
            + self.care_button.winfo_width()
        )
        button_bottom = (
            self.care_button.winfo_rooty()
            - self.root.winfo_rooty()
            + self.care_button.winfo_height()
        )
        panel.place(x=button_right, y=button_bottom + 6, width=470, anchor=tk.NE)
        panel.lift()
        self.care_button.configure(text="Cuidados  ▴")

    def _hide_care_panel(self, _event: tk.Event | None = None) -> None:
        panel = getattr(self, "_care_panel", None)
        if panel is not None and panel.winfo_exists():
            panel.place_forget()
        button = getattr(self, "care_button", None)
        if button is not None and button.winfo_exists():
            button.configure(text="Cuidados  ▾")

    def _start_care_action(self, request: str) -> None:
        self._hide_care_panel()
        if self._busy:
            return
        self.request_entry.delete(0, tk.END)
        self.request_entry.insert(0, request)
        self.submit()

    def _close_capabilities_on_outside_click(self, event: tk.Event) -> None:
        panel = getattr(self, "_resources_panel", None)
        automation_panel = getattr(self, "_automation_panel", None)
        automation_button = getattr(self, "automation_button", None)
        care_panel = getattr(self, "_care_panel", None)
        care_button = getattr(self, "care_button", None)
        remote_controls = getattr(self, "remote_controls", None)
        remote_button = getattr(self, "remote_controls_button", None)

        inside_resources = False
        inside_remote_controls = False
        inside_automation = False
        inside_care = False

        widget = event.widget
        while widget is not None:
            if widget is panel or widget is self.resources_button:
                inside_resources = True
            if widget is remote_controls or widget is remote_button:
                inside_remote_controls = True
            if widget is automation_panel or widget is automation_button:
                inside_automation = True
            if widget is care_panel or widget is care_button:
                inside_care = True
            widget = getattr(widget, "master", None)

        if panel is not None and panel.winfo_ismapped() and not inside_resources:
            self._hide_capabilities_panel()
        if self._remote_controls_visible and not inside_remote_controls:
            self._hide_remote_controls()
        if (
            automation_panel is not None
            and automation_panel.winfo_ismapped()
            and not inside_automation
        ):
            self._hide_automation_panel()
        if care_panel is not None and care_panel.winfo_ismapped() and not inside_care:
            self._hide_care_panel()
