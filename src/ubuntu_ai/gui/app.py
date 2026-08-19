from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from time import perf_counter

from ubuntu_ai.agent_loop.models import LoopSnapshot, LoopState
from ubuntu_ai.gui.backend import GUIBackend
from ubuntu_ai.interaction import ChatResponse, InteractionRoute

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

BACKGROUND = "#0d0f14"
SURFACE = "#171a21"
SURFACE_HOVER = "#1d2129"
SURFACE_ALT = "#20242d"
TERMINAL = "#0b0e13"

TEXT = "#f3f4f6"
TEXT_MUTED = "#9da4b3"
TEXT_DIM = "#707786"

ACCENT = "#8ab4f8"
ACCENT_HOVER = "#a8c7fa"

SUCCESS = "#81c995"
WARNING = "#fdd663"
ERROR = "#f28b82"

BORDER = "#2b3039"

CONTENT_PAD = 105


class UbuntuAIApp:
    """Interface desktop do Ubuntu AI Assistant."""

    def __init__(self) -> None:
        self._backend = GUIBackend()
        self._busy = False
        self._operation_generation = 0
        self._operation_started_at: dict[int, float] = {}
        self._active_actions: tk.Frame | None = None
        self._active_plan_card: tk.Frame | None = None

        self.root = tk.Tk()
        self.root.title("Ubuntu AI Assistant")
        self.root.geometry("1040x760")
        self.root.minsize(780, 580)
        self.root.configure(bg=BACKGROUND)
        self._set_window_icon()

        self._build_interface()
        self._bind_accessibility_shortcuts()
        self._show_welcome()

    @staticmethod
    def _icon_candidates() -> tuple[Path, ...]:
        return (
            Path.home() / ".local/share/icons/hicolor/512x512/apps/ubuntu-ai-assistant.png",
            Path(__file__).resolve().parent / "assets" / "ubuntu-ai-assistant.png",
        )

    def _set_window_icon(self) -> None:
        self._window_icon: tk.PhotoImage | None = None

        for icon_path in self._icon_candidates():
            if not icon_path.is_file():
                continue

            try:
                window_icon = tk.PhotoImage(file=icon_path)
            except (tk.TclError, OSError):
                continue

            self._window_icon = window_icon
            self.root.iconphoto(True, window_icon)
            return

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_interface(self) -> None:
        header = tk.Frame(
            self.root,
            bg=BACKGROUND,
            padx=30,
            pady=20,
        )
        header.pack(fill=tk.X)

        brand = tk.Frame(header, bg=BACKGROUND)
        brand.pack(side=tk.LEFT)

        if self._window_icon is not None:
            self._header_icon = self._window_icon.subsample(16, 16)
            tk.Label(
                brand,
                image=self._header_icon,
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
            font=("Sans", 15, "bold"),
        ).pack(side=tk.LEFT)

        tk.Label(
            brand,
            text="  Assistant",
            bg=BACKGROUND,
            fg=TEXT_MUTED,
            font=("Sans", 11),
        ).pack(side=tk.LEFT)

        self.status_label = tk.Label(
            header,
            text="●  Pronto",
            bg=BACKGROUND,
            fg=SUCCESS,
            font=("Sans", 10),
        )
        self.status_label.pack(side=tk.RIGHT)

        self.content = tk.Frame(
            self.root,
            bg=BACKGROUND,
        )
        self.content.pack(
            fill=tk.BOTH,
            expand=True,
            padx=28,
        )

        self.canvas = tk.Canvas(
            self.content,
            bg=BACKGROUND,
            highlightthickness=0,
            borderwidth=0,
        )

        self.scrollbar = tk.Scrollbar(
            self.content,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
            borderwidth=0,
            highlightthickness=0,
        )

        self.messages = tk.Frame(
            self.canvas,
            bg=BACKGROUND,
        )

        self.messages.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.messages,
            anchor="nw",
        )

        self.canvas.bind(
            "<Configure>",
            self._resize_messages,
        )

        self.canvas.configure(
            yscrollcommand=self.scrollbar.set,
        )

        self.canvas.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        self.scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

        # Composer ------------------------------------------------------

        self.composer_outer = tk.Frame(
            self.root,
            bg=BACKGROUND,
            padx=28,
            pady=12,
        )
        self.composer_outer.pack(
            fill=tk.X,
            pady=(0, 190),
        )

        self.composer = tk.Frame(
            self.composer_outer,
            bg=SURFACE_ALT,
            padx=18,
            pady=10,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        self.composer.pack(
            fill=tk.X,
            padx=CONTENT_PAD,
        )

        self.request_entry = tk.Entry(
            self.composer,
            bg=SURFACE_ALT,
            fg=TEXT,
            insertbackground=TEXT,
            disabledbackground=SURFACE_ALT,
            disabledforeground=TEXT_DIM,
            relief=tk.FLAT,
            borderwidth=0,
            font=("Sans", 12),
        )
        self.request_entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            ipady=9,
        )

        self.request_entry.bind(
            "<Return>",
            self._on_enter,
        )

        self.send_button = tk.Button(
            self.composer,
            text="Enviar",
            command=self.submit,
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
            font=("Sans", 10, "bold"),
        )
        self.send_button.pack(
            side=tk.RIGHT,
            padx=(14, 0),
        )

        self.request_entry.focus_set()

    def _show_welcome(self) -> None:
        self.welcome = tk.Frame(
            self.messages,
            bg=BACKGROUND,
        )
        self.welcome.pack(
            fill=tk.X,
            pady=(55, 24),
        )

        if self._window_icon is not None:
            self._welcome_icon = self._window_icon.subsample(4, 4)
            tk.Label(
                self.welcome,
                image=self._welcome_icon,
                bg=BACKGROUND,
                borderwidth=0,
            ).pack(pady=(0, 20))

        tk.Label(
            self.welcome,
            text="Como posso ajudar?",
            bg=BACKGROUND,
            fg=TEXT,
            font=("Sans", 30, "bold"),
        ).pack()

    # ------------------------------------------------------------------
    # Request
    # ------------------------------------------------------------------

    def submit(self) -> None:
        if self._busy:
            return

        request = self.request_entry.get().strip()

        if not request:
            return

        self.request_entry.delete(0, tk.END)

        if self.welcome.winfo_exists():
            self.welcome.destroy()
            self.composer_outer.pack_configure(pady=(0, 24))

        self._add_user_message(request)

        decision = self._backend.route(request)
        if decision.route is InteractionRoute.LOCAL:
            self._add_system_message(
                f"{decision.response}\n\nRota local · {self._format_duration(decision.duration)}",
                color=TEXT,
            )
            self.request_entry.focus_set()
            return

        if decision.route is InteractionRoute.CHAT:
            operation = self._begin_operation("Respondendo")
            threading.Thread(
                target=self._start_chat,
                args=(request, operation),
                daemon=True,
            ).start()
            return

        operation = self._begin_operation("Analisando")
        self._operation_started_at[operation] = perf_counter()

        threading.Thread(
            target=self._start_request,
            args=(request, operation),
            daemon=True,
        ).start()

    def _start_request(
        self,
        request: str,
        operation: int,
    ) -> None:
        try:
            snapshot = self._backend.start(request)
        except Exception as exc:
            self.root.after(
                0,
                self._deliver_error,
                operation,
                str(exc),
            )
            return

        self.root.after(
            0,
            self._deliver_snapshot,
            operation,
            snapshot,
        )

    def _start_chat(
        self,
        request: str,
        operation: int,
    ) -> None:
        try:
            response = self._backend.chat(request)
        except Exception as exc:
            self.root.after(0, self._deliver_error, operation, str(exc))
            return

        self.root.after(0, self._deliver_chat, operation, response)

    def _deliver_chat(
        self,
        operation: int,
        response: ChatResponse,
    ) -> None:
        if operation != self._operation_generation:
            return

        self._set_busy(False)
        self._add_system_message(
            f"{response.content}\n\nRota IA local · {response.model} · "
            f"{self._format_duration(response.duration)}",
            color=TEXT,
        )

    def _deliver_snapshot(
        self,
        operation: int,
        snapshot: LoopSnapshot,
    ) -> None:
        if operation != self._operation_generation:
            return

        started = getattr(self, "_operation_started_at", {}).pop(operation, None)
        if started is not None:
            self._add_system_message(
                f"Rota ação segura · {self._format_duration(perf_counter() - started)}",
                color=TEXT_MUTED,
            )

        self._show_snapshot(snapshot)

    def _deliver_error(
        self,
        operation: int,
        message: str,
    ) -> None:
        if operation != self._operation_generation:
            return

        self._show_error(message)

    def _show_snapshot(self, snapshot: LoopSnapshot) -> None:
        # Planos LOW podem ser executados automaticamente pelo controller.
        # Nesse caso, o snapshot já retorna com os resultados da execução.
        if snapshot.records:
            self._show_execution(snapshot)
            return

        self._set_busy(False)

        pending = snapshot.pending_plan

        if pending is not None and pending.pipeline_result is not None:
            plan = pending.pipeline_result.plan

            if plan is not None:
                self._add_plan_card(
                    snapshot,
                    plan,
                )
                return

        self._add_system_message(
            self._state_message(snapshot),
        )

    # ------------------------------------------------------------------
    # Conversation
    # ------------------------------------------------------------------

    def _add_user_message(self, message: str) -> None:
        frame = tk.Frame(
            self.messages,
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
            font=("Sans", 11),
            justify=tk.LEFT,
            wraplength=560,
            padx=17,
            pady=12,
        )
        bubble.pack(side=tk.RIGHT)

        self._scroll_bottom()

    def _add_system_message(
        self,
        message: str,
        *,
        color: str = TEXT,
    ) -> None:
        frame = tk.Frame(
            self.messages,
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
            font=("Sans", 11),
            justify=tk.LEFT,
            wraplength=650,
        ).pack(anchor="w")

        self._scroll_bottom()

    # ------------------------------------------------------------------
    # Plan
    # ------------------------------------------------------------------

    def _add_plan_card(
        self,
        snapshot: LoopSnapshot,
        plan: object,
    ) -> None:
        outer = tk.Frame(
            self.messages,
            bg=BACKGROUND,
        )
        outer.pack(
            fill=tk.X,
            padx=CONTENT_PAD,
            pady=18,
        )

        self._active_plan_card = outer

        card = tk.Frame(
            outer,
            bg=SURFACE,
            padx=24,
            pady=21,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        card.pack(fill=tk.X)

        risk = getattr(plan, "risk", None)
        risk_value = str(getattr(risk, "value", risk) or "unknown")

        header = tk.Frame(
            card,
            bg=SURFACE,
        )
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text=str(
                getattr(
                    plan,
                    "goal",
                    "Plano proposto",
                )
            ),
            bg=SURFACE,
            fg=TEXT,
            font=("Sans", 15, "bold"),
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text=self._risk_label(risk_value),
            bg=SURFACE,
            fg=self._risk_color(risk_value),
            font=("Sans", 10, "bold"),
        ).pack(side=tk.RIGHT)

        planner = getattr(plan, "planner", None)

        if planner:
            tk.Label(
                card,
                text=f"Planejador · {planner}",
                bg=SURFACE,
                fg=TEXT_MUTED,
                font=("Sans", 9),
            ).pack(
                anchor="w",
                pady=(6, 15),
            )

        steps = getattr(plan, "steps", ()) or ()

        for index, step in enumerate(
            steps,
            start=1,
        ):
            title = getattr(
                step,
                "title",
                f"Etapa {index}",
            )

            tk.Label(
                card,
                text=f"{index}. {title}",
                bg=SURFACE,
                fg=TEXT,
                font=("Sans", 11, "bold"),
            ).pack(
                anchor="w",
                pady=(8, 3),
            )

            description = getattr(
                step,
                "description",
                "",
            )

            if description:
                tk.Label(
                    card,
                    text=description,
                    bg=SURFACE,
                    fg=TEXT_MUTED,
                    justify=tk.LEFT,
                    wraplength=640,
                    font=("Sans", 10),
                ).pack(anchor="w")

            command = getattr(
                step,
                "command",
                (),
            )

            if command:
                command_text = self._command_text(command)

                command_box = tk.Label(
                    card,
                    text=f"$ {command_text}",
                    bg=TERMINAL,
                    fg=SUCCESS,
                    justify=tk.LEFT,
                    anchor="w",
                    font=("Monospace", 10),
                    padx=14,
                    pady=11,
                )
                command_box.pack(
                    fill=tk.X,
                    pady=(10, 5),
                )

        if snapshot.requires_confirmation:
            actions = tk.Frame(
                card,
                bg=SURFACE,
            )
            actions.pack(
                fill=tk.X,
                pady=(20, 0),
            )

            self._active_actions = actions

            cancel_button = tk.Button(
                actions,
                text="Cancelar",
                command=self.cancel,
                bg=SURFACE_ALT,
                fg=TEXT,
                activebackground=SURFACE_HOVER,
                activeforeground=TEXT,
                relief=tk.FLAT,
                borderwidth=0,
                padx=20,
                pady=9,
                cursor="hand2",
                takefocus=True,
                font=("Sans", 10),
            )
            cancel_button.pack(
                side=tk.RIGHT,
                padx=(9, 0),
            )

            confirm_button = tk.Button(
                actions,
                text="Confirmar e executar",
                command=self.confirm,
                bg=ACCENT,
                fg="#101318",
                activebackground=ACCENT_HOVER,
                activeforeground="#101318",
                relief=tk.FLAT,
                borderwidth=0,
                padx=20,
                pady=9,
                cursor="hand2",
                takefocus=True,
                font=("Sans", 10, "bold"),
            )
            confirm_button.pack(side=tk.RIGHT)

        self._scroll_bottom()

    # ------------------------------------------------------------------
    # Confirmation / execution
    # ------------------------------------------------------------------

    def confirm(self) -> None:
        if self._busy:
            return

        self._remove_active_plan_card()
        operation = self._begin_operation("Executando")

        threading.Thread(
            target=self._confirm_request,
            args=(operation,),
            daemon=True,
        ).start()

    def _confirm_request(
        self,
        operation: int,
    ) -> None:
        try:
            snapshot = self._backend.confirm()
        except Exception as exc:
            self.root.after(
                0,
                self._deliver_error,
                operation,
                str(exc),
            )
            return

        self.root.after(
            0,
            self._deliver_execution,
            operation,
            snapshot,
        )

    def _deliver_execution(
        self,
        operation: int,
        snapshot: LoopSnapshot,
    ) -> None:
        if operation != self._operation_generation:
            return

        self._show_execution(snapshot)

    def _show_execution(
        self,
        snapshot: LoopSnapshot,
    ) -> None:
        self._set_busy(False)

        if snapshot.records:
            record = snapshot.records[-1]

            for result in record.execution_results:
                self._add_execution_result(result)

        if snapshot.requires_confirmation:
            pending = snapshot.pending_plan

            if pending is not None and pending.pipeline_result is not None:
                plan = pending.pipeline_result.plan

                if plan is not None:
                    self._add_plan_card(
                        snapshot,
                        plan,
                    )
                    return

        # O card de execução já apresenta o resultado final.
        # Evita mensagem redundante abaixo do card.
        if snapshot.state is not LoopState.COMPLETED:
            self._add_system_message(
                self._state_message(snapshot),
            )

    def _add_execution_result(
        self,
        result: object,
    ) -> None:
        status = getattr(
            result,
            "status",
            None,
        )
        status_value = str(
            getattr(
                status,
                "value",
                status,
            )
        ).lower()

        command = getattr(
            result,
            "command",
            None,
        )
        message = getattr(
            result,
            "message",
            "",
        )
        stdout = getattr(
            result,
            "stdout",
            "",
        )
        stderr = getattr(
            result,
            "stderr",
            "",
        )
        return_code = getattr(
            result,
            "return_code",
            None,
        )

        outer = tk.Frame(
            self.messages,
            bg=BACKGROUND,
        )
        outer.pack(
            fill=tk.X,
            padx=CONTENT_PAD,
            pady=12,
        )

        card = tk.Frame(
            outer,
            bg=SURFACE,
            padx=22,
            pady=18,
            highlightbackground=BORDER,
            highlightthickness=1,
        )
        card.pack(fill=tk.X)

        successful = status_value in {
            "approved",
            "executed",
            "success",
            "succeeded",
        }

        tk.Label(
            card,
            text=("✓ Execução concluída" if successful else "⚠ Execução não concluída"),
            bg=SURFACE,
            fg=(SUCCESS if successful else ERROR),
            font=("Sans", 12, "bold"),
        ).pack(anchor="w")

        if command:
            tk.Label(
                card,
                text=f"$ {command}",
                bg=TERMINAL,
                fg=SUCCESS,
                font=("Monospace", 10),
                anchor="w",
                padx=14,
                pady=11,
            ).pack(
                fill=tk.X,
                pady=(14, 9),
            )

        if message:
            tk.Label(
                card,
                text=str(message),
                bg=SURFACE,
                fg=TEXT_MUTED,
                justify=tk.LEFT,
                wraplength=640,
                font=("Sans", 10),
            ).pack(anchor="w")

        output = stdout or stderr

        if output:
            terminal_frame = tk.Frame(
                card,
                bg=TERMINAL,
                padx=1,
                pady=1,
            )
            terminal_frame.pack(
                fill=tk.X,
                pady=(13, 0),
            )

            text = tk.Text(
                terminal_frame,
                bg=TERMINAL,
                fg=TEXT,
                insertbackground=TEXT,
                selectbackground=SURFACE_ALT,
                relief=tk.FLAT,
                borderwidth=0,
                highlightthickness=0,
                font=("Monospace", 9),
                height=min(
                    max(
                        len(str(output).splitlines()),
                        3,
                    ),
                    14,
                ),
                wrap=tk.NONE,
                padx=12,
                pady=10,
            )

            text.insert(
                "1.0",
                str(output),
            )
            text.configure(
                state=tk.DISABLED,
            )

            text.pack(
                fill=tk.X,
            )

        if return_code is not None:
            tk.Label(
                card,
                text=(f"Concluído · código de saída {return_code}"),
                bg=SURFACE,
                fg=(SUCCESS if return_code == 0 else ERROR),
                font=("Sans", 8),
            ).pack(
                anchor="e",
                pady=(9, 0),
            )

        self._scroll_bottom()

    # ------------------------------------------------------------------
    # Cancel / errors
    # ------------------------------------------------------------------

    def cancel_current_operation(self) -> None:
        if not self._busy:
            return

        self._operation_generation += 1
        getattr(self, "_operation_started_at", {}).clear()

        try:
            self._backend.cancel()
        except RuntimeError:
            pass

        self._set_busy(False)
        self._add_system_message(
            "Operação cancelada. Você já pode enviar uma nova solicitação.",
            color=WARNING,
        )

    def cancel(self) -> None:
        if self._busy:
            return

        self._close_active_actions("Plano cancelado")

        try:
            snapshot = self._backend.cancel()
        except Exception as exc:
            self._show_error(str(exc))
            return

        self._add_system_message(
            self._state_message(snapshot),
            color=TEXT_MUTED,
        )

    def _show_error(
        self,
        message: str,
    ) -> None:
        self._set_busy(False)

        friendly_message = self._friendly_error(message)
        self._add_system_message(
            f"Não foi possível concluir a solicitação.\n{friendly_message}",
            color=ERROR,
        )

        self.status_label.configure(
            text="●  Erro",
            fg=ERROR,
        )

    @staticmethod
    def _friendly_error(message: str) -> str:
        normalized = message.strip().lower()

        if not normalized:
            return "O backend não informou detalhes. Tente novamente."

        if "ollama" in normalized or "connection refused" in normalized:
            return "Não foi possível conectar ao Ollama. Verifique se o serviço está em execução."

        if "timeout" in normalized or "timed out" in normalized:
            return (
                "A operação excedeu o tempo esperado. "
                "Você pode tentar novamente com uma solicitação mais direta."
            )

        if "model" in normalized and ("not found" in normalized or "não encontrado" in normalized):
            return (
                "O modelo de IA configurado não foi encontrado. "
                "Confira os modelos disponíveis no Ollama."
            )

        if "permission denied" in normalized or "permissão negada" in normalized:
            return (
                "O Ubuntu negou permissão para essa operação. "
                "Revise o plano e as permissões necessárias."
            )

        return message.strip()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _remove_active_plan_card(self) -> None:
        """Remove o plano visual após sua confirmação."""

        card = self._active_plan_card

        if card is not None and card.winfo_exists():
            card.destroy()

        self._active_plan_card = None
        self._active_actions = None

    def _close_active_actions(
        self,
        message: str,
    ) -> None:
        actions = self._active_actions

        if actions is None or not actions.winfo_exists():
            self._active_actions = None
            return

        for child in actions.winfo_children():
            child.destroy()

        tk.Label(
            actions,
            text=message,
            bg=SURFACE,
            fg=TEXT_MUTED,
            font=("Sans", 9),
        ).pack(side=tk.RIGHT)

        self._active_actions = None

    def _begin_operation(
        self,
        label: str,
    ) -> int:
        self._operation_generation += 1
        self._set_busy(True, label)
        return self._operation_generation

    @staticmethod
    def _format_duration(duration: float) -> str:
        if duration < 0.001:
            return f"{duration * 1_000_000:.0f} µs"
        if duration < 1.0:
            return f"{duration * 1000:.1f} ms"
        return f"{duration:.2f} s"

    def _set_busy(
        self,
        busy: bool,
        label: str = "Pronto",
    ) -> None:
        self._busy = busy

        if busy:
            self.status_label.configure(
                text=f"●  {label}...",
                fg=WARNING,
            )
            self.send_button.configure(
                text="Interromper",
                command=self.cancel_current_operation,
                state=tk.NORMAL,
                bg=WARNING,
            )
            self.request_entry.configure(
                state=tk.DISABLED,
            )
        else:
            self.status_label.configure(
                text="●  Pronto",
                fg=SUCCESS,
            )
            self.send_button.configure(
                text="Enviar",
                command=self.submit,
                state=tk.NORMAL,
                bg=ACCENT,
            )
            self.request_entry.configure(
                state=tk.NORMAL,
            )
            self.request_entry.focus_set()

    @staticmethod
    def _command_text(
        command: object,
    ) -> str:
        if isinstance(
            command,
            (list, tuple),
        ):
            return " ".join(str(item) for item in command)

        return str(command)

    @staticmethod
    def _state_message(
        snapshot: LoopSnapshot,
    ) -> str:
        messages = {
            LoopState.COMPLETED: "✓ Operação concluída com sucesso.",
            LoopState.BLOCKED: "A operação foi bloqueada pela política de segurança.",
            LoopState.FAILED: "Não foi possível concluir a operação.",
            LoopState.CANCELLED: "Operação cancelada.",
            LoopState.WAITING_CONFIRMATION: "O plano aguarda sua confirmação.",
        }

        return messages.get(
            snapshot.state,
            f"Estado: {snapshot.state.value}",
        )

    @staticmethod
    def _risk_label(
        risk: str,
    ) -> str:
        labels = {
            "low": "Risco baixo",
            "medium": "Risco médio",
            "high": "Risco alto",
            "critical": "Risco crítico",
        }

        normalized = risk.lower()

        return labels.get(
            normalized,
            f"Risco {risk}",
        )

    @staticmethod
    def _risk_color(
        risk: str,
    ) -> str:
        normalized = risk.lower()

        if normalized == "low":
            return SUCCESS

        if normalized == "medium":
            return WARNING

        return ERROR

    def _resize_messages(
        self,
        event: tk.Event,
    ) -> None:
        self.canvas.itemconfigure(
            self.canvas_window,
            width=event.width,
        )

    def _scroll_bottom(self) -> None:
        self.root.after(
            30,
            lambda: self.canvas.yview_moveto(1.0),
        )

    def _bind_accessibility_shortcuts(self) -> None:
        self.root.bind("<Escape>", self._on_escape)
        self.root.bind("<Control-l>", self._focus_request)
        self.root.bind("<Control-L>", self._focus_request)

    def _on_escape(
        self,
        _event: tk.Event | None = None,
    ) -> str:
        if self._busy:
            self.cancel_current_operation()
        else:
            self.request_entry.focus_set()

        return "break"

    def _focus_request(
        self,
        _event: tk.Event | None = None,
    ) -> str:
        if not self._busy:
            self.request_entry.focus_set()

        return "break"

    def _on_enter(
        self,
        _event: tk.Event,
    ) -> None:
        self.submit()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    UbuntuAIApp().run()


if __name__ == "__main__":
    main()
