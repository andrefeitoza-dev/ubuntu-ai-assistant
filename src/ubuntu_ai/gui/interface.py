from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass

from ubuntu_ai.gui.remote_controls import build_remote_controls
from ubuntu_ai.gui.theme import (
    ACCENT,
    ACCENT_HOVER,
    BACKGROUND,
    BORDER,
    CONTENT_PAD,
    FONT_BODY,
    FONT_SMALL,
    FONT_SMALL_BOLD,
    FONT_TINY,
    FONT_TITLE,
    SUCCESS,
    SURFACE_ALT,
    SURFACE_HOVER,
    TEXT,
    TEXT_DIM,
    TEXT_MUTED,
    WARNING,
)


@dataclass(frozen=True, slots=True)
class InterfaceWidgets:
    header_icon: tk.PhotoImage | None
    status_label: tk.Label
    care_button: tk.Button
    resources_button: tk.Button
    automation_button: tk.Button
    remote_controls_button: tk.Button
    remote_controls: tk.Frame
    target_variable: tk.StringVar
    target_menu: tk.OptionMenu
    content: tk.Frame
    canvas: tk.Canvas
    scrollbar: tk.Scrollbar
    messages: tk.Frame
    canvas_window: int
    composer_outer: tk.Frame
    composer: tk.Frame
    request_entry: tk.Entry
    voice_button: tk.Button
    send_button: tk.Button


def bind_hover_reveal(
    widget: tk.Widget,
    *,
    foreground: str | Callable[[], str],
    visible_background: str = BACKGROUND,
) -> None:
    """Mantém o controle discreto até hover ou foco pelo teclado."""

    state = {"pointer": False, "focus": False}

    def visible_foreground() -> str:
        return foreground() if callable(foreground) else foreground

    def refresh() -> None:
        visible = state["pointer"] or state["focus"]
        widget.configure(
            fg=visible_foreground() if visible else BACKGROUND,
            bg=visible_background if visible else BACKGROUND,
        )

    def set_state(name: str, value: bool) -> None:
        state[name] = value
        refresh()

    widget.bind("<Enter>", lambda _event: set_state("pointer", True), add="+")
    widget.bind("<Leave>", lambda _event: set_state("pointer", False), add="+")
    widget.bind("<FocusIn>", lambda _event: set_state("focus", True), add="+")
    widget.bind("<FocusOut>", lambda _event: set_state("focus", False), add="+")
    refresh()


def scroll_canvas_bottom(root: tk.Misc, canvas: tk.Canvas) -> None:
    """Rola após o Tk calcular a geometria de cards recém-adicionados."""

    def apply() -> None:
        root.update_idletasks()
        bounds = canvas.bbox("all")
        if bounds is not None:
            canvas.configure(scrollregion=bounds)
        canvas.yview_moveto(1.0)

    root.after_idle(apply)
    root.after(80, apply)


def build_main_interface(
    root: tk.Misc,
    *,
    window_icon: tk.PhotoImage | None,
    on_show_capabilities: Callable[[], None],
    on_show_care: Callable[[], None],
    on_show_automation: Callable[[], None],
    on_toggle_remote: Callable[[], None],
    on_target_selected: Callable[..., object],
    on_add_remote: Callable[[], None],
    on_remove_remote: Callable[[], None],
    on_diagnose_remote: Callable[[], None],
    on_resize_messages: Callable[..., object],
    on_enter: Callable[..., object],
    on_voice: Callable[[], None],
    on_submit: Callable[[], None],
) -> InterfaceWidgets:
    header = tk.Frame(
        root,
        bg=BACKGROUND,
        padx=30,
        pady=20,
    )
    header.pack(fill=tk.X)

    brand = tk.Frame(header, bg=BACKGROUND)
    brand.pack(side=tk.LEFT)

    header_icon: tk.PhotoImage | None = None
    if window_icon is not None:
        header_icon = window_icon.subsample(16, 16)
        tk.Label(
            brand,
            image=header_icon,
            bg=BACKGROUND,
            borderwidth=0,
        ).pack(
            side=tk.LEFT,
            padx=(0, 10),
        )

    tk.Label(
        brand,
        text="Ubuntu AI",
        bg=BACKGROUND,
        fg=TEXT,
        font=FONT_TITLE,
    ).pack(side=tk.LEFT)

    tk.Label(
        brand,
        text="  Assistant",
        bg=BACKGROUND,
        fg=TEXT_MUTED,
        font=FONT_BODY,
    ).pack(side=tk.LEFT)

    status_label = tk.Label(
        header,
        text="●  Pronto",
        bg=BACKGROUND,
        fg=SUCCESS,
        font=FONT_SMALL,
    )
    status_label.pack(side=tk.RIGHT)

    care_button = tk.Button(
        header,
        text="Cuidados  ▾",
        command=on_show_care,
        bg=BACKGROUND,
        fg=TEXT_MUTED,
        activebackground=SURFACE_HOVER,
        activeforeground=TEXT,
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        takefocus=True,
        font=FONT_TINY,
        padx=8,
        pady=4,
    )
    care_button.pack(side=tk.RIGHT, padx=(0, 10))

    resources_button = tk.Button(
        header,
        text="Recursos e ajuda  ▾",
        command=on_show_capabilities,
        bg=BACKGROUND,
        fg=TEXT_MUTED,
        activebackground=SURFACE_HOVER,
        activeforeground=TEXT,
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        takefocus=True,
        font=FONT_TINY,
        padx=8,
        pady=4,
    )
    resources_button.pack(side=tk.RIGHT, padx=(0, 10))

    automation_button = tk.Button(
        header,
        text="Agentes e progresso  ▾",
        command=on_show_automation,
        bg=BACKGROUND,
        fg=TEXT_MUTED,
        activebackground=SURFACE_HOVER,
        activeforeground=TEXT,
        relief=tk.FLAT,
        borderwidth=0,
        highlightthickness=0,
        cursor="hand2",
        takefocus=True,
        font=FONT_TINY,
        padx=8,
        pady=4,
    )
    automation_button.pack(side=tk.RIGHT, padx=(0, 10))

    remote_widgets = build_remote_controls(
        header,
        on_toggle=on_toggle_remote,
        on_target_selected=on_target_selected,
        on_add=on_add_remote,
        on_remove=on_remove_remote,
        on_diagnose=on_diagnose_remote,
    )

    content = tk.Frame(root, bg=BACKGROUND)
    content.pack(
        fill=tk.BOTH,
        expand=True,
        padx=28,
    )

    canvas = tk.Canvas(
        content,
        bg=BACKGROUND,
        highlightthickness=0,
        borderwidth=0,
    )

    scrollbar = tk.Scrollbar(
        content,
        orient=tk.VERTICAL,
        command=canvas.yview,
        borderwidth=0,
        highlightthickness=0,
    )

    messages = tk.Frame(canvas, bg=BACKGROUND)

    messages.bind(
        "<Configure>",
        lambda _event: canvas.configure(scrollregion=canvas.bbox("all")),
    )

    canvas_window = canvas.create_window(
        (0, 0),
        window=messages,
        anchor="nw",
    )

    canvas.bind("<Configure>", on_resize_messages)
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(
        side=tk.LEFT,
        fill=tk.BOTH,
        expand=True,
    )

    scrollbar.pack(
        side=tk.RIGHT,
        fill=tk.Y,
    )

    composer_outer = tk.Frame(
        root,
        bg=BACKGROUND,
        padx=28,
        pady=12,
    )
    composer_outer.pack(
        fill=tk.X,
        pady=(0, 190),
    )

    composer = tk.Frame(
        composer_outer,
        bg=SURFACE_ALT,
        padx=18,
        pady=10,
        highlightbackground=BORDER,
        highlightthickness=1,
    )
    composer.pack(
        fill=tk.X,
        padx=CONTENT_PAD,
    )

    request_entry = tk.Entry(
        composer,
        bg=SURFACE_ALT,
        fg=TEXT,
        insertbackground=TEXT,
        disabledbackground=SURFACE_ALT,
        disabledforeground=TEXT_DIM,
        relief=tk.FLAT,
        borderwidth=0,
        font=FONT_BODY,
    )
    request_entry.pack(
        side=tk.LEFT,
        fill=tk.X,
        expand=True,
        ipady=9,
    )
    request_entry.bind("<Return>", on_enter)

    voice_button = tk.Button(
        composer,
        text="Falar",
        command=on_voice,
        bg=SURFACE_ALT,
        fg=TEXT_MUTED,
        activebackground=SURFACE_HOVER,
        activeforeground=TEXT,
        relief=tk.FLAT,
        borderwidth=0,
        padx=14,
        pady=9,
        cursor="hand2",
        takefocus=True,
        font=FONT_SMALL_BOLD,
    )
    send_button = tk.Button(
        composer,
        text="Enviar",
        command=on_submit,
        bg=ACCENT,
        fg="#101318",
        activebackground=ACCENT_HOVER,
        activeforeground="#101318",
        disabledforeground=TEXT_DIM,
        relief=tk.FLAT,
        borderwidth=0,
        padx=20,
        pady=9,
        cursor="hand2",
        takefocus=True,
        font=FONT_SMALL_BOLD,
    )
    send_button.pack(
        side=tk.RIGHT,
        padx=(14, 0),
    )
    voice_button.pack(side=tk.RIGHT, padx=(12, 0))

    request_entry.focus_set()

    return InterfaceWidgets(
        header_icon=header_icon,
        status_label=status_label,
        care_button=care_button,
        resources_button=resources_button,
        automation_button=automation_button,
        remote_controls_button=remote_widgets.button,
        remote_controls=remote_widgets.container,
        target_variable=remote_widgets.target_variable,
        target_menu=remote_widgets.target_menu,
        content=content,
        canvas=canvas,
        scrollbar=scrollbar,
        messages=messages,
        canvas_window=canvas_window,
        composer_outer=composer_outer,
        composer=composer,
        request_entry=request_entry,
        voice_button=voice_button,
        send_button=send_button,
    )


def apply_busy_state(
    *,
    busy: bool,
    label: str,
    status_label: object,
    send_button: object,
    request_entry: object,
    on_submit: Callable[[], None],
    on_cancel: Callable[[], None],
) -> None:
    if busy:
        status_label.configure(
            text=f"●  {label}...",
            fg=WARNING,
        )
        send_button.configure(
            text="Interromper",
            command=on_cancel,
            state=tk.NORMAL,
            bg=WARNING,
        )
        request_entry.configure(state=tk.DISABLED)
        return

    status_label.configure(
        text="●  Pronto",
        fg=SUCCESS,
    )
    send_button.configure(
        text="Enviar",
        command=on_submit,
        state=tk.NORMAL,
        bg=ACCENT,
    )
    request_entry.configure(state=tk.NORMAL)
    request_entry.focus_set()
