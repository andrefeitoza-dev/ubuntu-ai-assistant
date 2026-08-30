from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass

from ubuntu_ai.agent_loop.models import LoopSnapshot
from ubuntu_ai.gui.presentation import command_text, risk_color, risk_label
from ubuntu_ai.gui.theme import (
    ACCENT,
    BACKGROUND,
    BORDER,
    ERROR,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_MONO,
    FONT_SMALL,
    FONT_SMALL_BOLD,
    FONT_TINY,
    SUCCESS,
    SURFACE,
    SURFACE_ALT,
    TEXT,
    TEXT_DIM,
    TEXT_MUTED,
    WARNING,
)


@dataclass(frozen=True, slots=True)
class PlanCardWidgets:
    outer: tk.Frame
    actions: tk.Frame | None


def execution_status_value(result: object) -> str:
    status = getattr(result, "status", "")
    return str(getattr(status, "value", status)).lower()


def execution_succeeded(result: object) -> bool:
    return execution_status_value(result) in {
        "approved",
        "executed",
        "success",
        "succeeded",
    }


def execution_output(result: object) -> str:
    stdout = str(getattr(result, "stdout", "") or "")
    stderr = str(getattr(result, "stderr", "") or "")
    return stdout or stderr


def plan_risk_tone(risk: object) -> str:
    return risk_color(str(risk), success=SUCCESS, warning=WARNING, error=ERROR)


def build_plan_card(
    parent: tk.Misc,
    *,
    snapshot: LoopSnapshot,
    plan: object,
    on_confirm: Callable[[], None],
    on_cancel: Callable[[], None],
) -> PlanCardWidgets:
    outer = tk.Frame(
        parent,
        bg=SURFACE,
        highlightbackground=BORDER,
        highlightthickness=1,
        padx=16,
        pady=14,
    )
    outer.pack(fill=tk.X, pady=(0, 12))

    risk = getattr(plan, "risk", None)
    risk_name = risk_label(risk)
    risk_tone = plan_risk_tone(risk)

    header = tk.Frame(outer, bg=SURFACE)
    header.pack(fill=tk.X)

    tk.Label(
        header,
        text="PLANO DE EXECUÇÃO",
        bg=SURFACE,
        fg=TEXT_MUTED,
        font=FONT_TINY,
    ).pack(side=tk.LEFT)

    tk.Label(
        header,
        text=risk_name,
        bg=risk_tone,
        fg=BACKGROUND,
        font=FONT_SMALL_BOLD,
        padx=8,
        pady=3,
    ).pack(side=tk.RIGHT)

    goal = str(getattr(plan, "goal", "") or "")
    if goal:
        tk.Label(
            outer,
            text=goal,
            bg=SURFACE,
            fg=TEXT,
            font=FONT_BODY_BOLD,
            anchor="w",
            justify=tk.LEFT,
            wraplength=760,
        ).pack(fill=tk.X, pady=(12, 8))

    planner = str(getattr(plan, "planner", "") or "")
    estimated = getattr(plan, "estimated_seconds", None)
    metadata = []

    if planner:
        metadata.append(f"Planejador: {planner}")

    if estimated is not None:
        metadata.append(f"Estimativa: {estimated}s")

    if metadata:
        tk.Label(
            outer,
            text=" · ".join(metadata),
            bg=SURFACE,
            fg=TEXT_DIM,
            font=FONT_SMALL,
            anchor="w",
        ).pack(fill=tk.X, pady=(0, 10))

    steps = tuple(getattr(plan, "steps", ()) or ())
    for index, step in enumerate(steps, start=1):
        step_box = tk.Frame(outer, bg=SURFACE_ALT, padx=10, pady=8)
        step_box.pack(fill=tk.X, pady=3)

        title = str(getattr(step, "title", "") or f"Etapa {index}")
        tk.Label(
            step_box,
            text=f"{index}. {title}",
            bg=SURFACE_ALT,
            fg=TEXT,
            font=FONT_BODY,
            anchor="w",
            justify=tk.LEFT,
            wraplength=720,
        ).pack(fill=tk.X)

        command = command_text(getattr(step, "command", ""))
        if command:
            tk.Label(
                step_box,
                text=f"$ {command}",
                bg=SURFACE_ALT,
                fg=ACCENT,
                font=FONT_MONO,
                anchor="w",
                justify=tk.LEFT,
                wraplength=720,
            ).pack(fill=tk.X, pady=(5, 0))

    actions: tk.Frame | None = None

    if snapshot.requires_confirmation:
        actions = tk.Frame(outer, bg=SURFACE)
        actions.pack(fill=tk.X, pady=(14, 0))

        tk.Button(
            actions,
            text="Confirmar",
            command=on_confirm,
            bg=ACCENT,
            fg=BACKGROUND,
            activebackground=SUCCESS,
            activeforeground=BACKGROUND,
            relief=tk.FLAT,
            font=FONT_SMALL_BOLD,
            padx=14,
            pady=7,
            cursor="hand2",
        ).pack(side=tk.LEFT)

        tk.Button(
            actions,
            text="Cancelar",
            command=on_cancel,
            bg=SURFACE_ALT,
            fg=TEXT,
            activebackground=ERROR,
            activeforeground=TEXT,
            relief=tk.FLAT,
            font=FONT_SMALL_BOLD,
            padx=14,
            pady=7,
            cursor="hand2",
        ).pack(side=tk.LEFT, padx=(8, 0))

    return PlanCardWidgets(outer=outer, actions=actions)


def build_execution_result_card(
    parent: tk.Misc,
    *,
    result: object,
) -> tk.Frame:
    succeeded = execution_succeeded(result)
    tone = SUCCESS if succeeded else ERROR
    status = execution_status_value(result).upper()
    command = str(getattr(result, "command", "") or "")
    message = str(getattr(result, "message", "") or "")
    return_code = getattr(result, "return_code", None)
    output = execution_output(result)

    outer = tk.Frame(
        parent,
        bg=SURFACE,
        highlightbackground=tone,
        highlightthickness=1,
        padx=16,
        pady=14,
    )
    outer.pack(fill=tk.X, pady=(0, 12))

    header = tk.Frame(outer, bg=SURFACE)
    header.pack(fill=tk.X)

    tk.Label(
        header,
        text="RESULTADO DA EXECUÇÃO",
        bg=SURFACE,
        fg=TEXT_MUTED,
        font=FONT_TINY,
    ).pack(side=tk.LEFT)

    tk.Label(
        header,
        text=status,
        bg=tone,
        fg=BACKGROUND,
        font=FONT_SMALL_BOLD,
        padx=8,
        pady=3,
    ).pack(side=tk.RIGHT)

    if command:
        tk.Label(
            outer,
            text=f"$ {command}",
            bg=SURFACE,
            fg=ACCENT,
            font=FONT_MONO,
            anchor="w",
            justify=tk.LEFT,
            wraplength=760,
        ).pack(fill=tk.X, pady=(12, 6))

    if message:
        tk.Label(
            outer,
            text=message,
            bg=SURFACE,
            fg=TEXT,
            font=FONT_BODY,
            anchor="w",
            justify=tk.LEFT,
            wraplength=760,
        ).pack(fill=tk.X, pady=(4, 8))

    if output:
        terminal = tk.Text(
            outer,
            height=min(max(output.count("\n") + 1, 3), 12),
            bg=BACKGROUND,
            fg=TEXT,
            insertbackground=TEXT,
            relief=tk.FLAT,
            font=FONT_MONO,
            padx=10,
            pady=8,
            wrap=tk.WORD,
        )
        terminal.insert("1.0", output)
        terminal.configure(state=tk.DISABLED)
        terminal.pack(fill=tk.X, pady=(4, 8))

    if return_code is not None:
        tk.Label(
            outer,
            text=f"Código de retorno: {return_code}",
            bg=SURFACE,
            fg=TEXT_DIM,
            font=FONT_SMALL,
            anchor="w",
        ).pack(fill=tk.X)

    return outer
