from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from queue import Empty, SimpleQueue
from time import perf_counter
from tkinter import messagebox, simpledialog

from ubuntu_ai.agent_loop.models import LoopSnapshot, LoopState
from ubuntu_ai.gui.automation_panel import (
    build_automation_panel,
    summary_text,
    task_row,
)
from ubuntu_ai.gui.backend import GUIBackend, MultiAgentExecutionReport
from ubuntu_ai.gui.capabilities_panel import build_capabilities_panel
from ubuntu_ai.gui.conversation_view import (
    add_system_message,
    add_user_message,
    build_welcome,
)
from ubuntu_ai.gui.execution_cards import (
    build_execution_result_card,
    build_plan_card,
)
from ubuntu_ai.gui.first_run_controller import FirstRunControllerMixin
from ubuntu_ai.gui.interface import (
    apply_busy_state,
    bind_hover_reveal,
    build_main_interface,
    scroll_canvas_bottom,
)
from ubuntu_ai.gui.panel_controller import PanelControllerMixin
from ubuntu_ai.gui.presentation import (
    command_text,
    format_duration,
    friendly_error,
    risk_color,
    risk_label,
    state_message,
)
from ubuntu_ai.gui.remote_controls import (
    place_remote_controls,
    remote_button_text,
)
from ubuntu_ai.gui.single_instance import SingleInstance
from ubuntu_ai.gui.theme import (
    BACKGROUND,
    ERROR,
    FONT_TINY,
    SUCCESS,
    SURFACE,
    SURFACE_ALT,
    TEXT,
    TEXT_MUTED,
    WARNING,
    WINDOW_CLASS,
)
from ubuntu_ai.gui.theme import (
    FONT_BODY as FONT_BODY,
)
from ubuntu_ai.gui.theme import (
    FONT_BODY_BOLD as FONT_BODY_BOLD,
)
from ubuntu_ai.gui.theme import (
    FONT_MONO as FONT_MONO,
)
from ubuntu_ai.gui.theme import (
    FONT_MONO_SMALL as FONT_MONO_SMALL,
)
from ubuntu_ai.gui.theme import (
    FONT_SMALL as FONT_SMALL,
)
from ubuntu_ai.gui.theme import (
    TERMINAL as TERMINAL,
)
from ubuntu_ai.gui.voice_controller import VoiceControllerMixin
from ubuntu_ai.interaction import ChatResponse, InteractionRoute
from ubuntu_ai.remote.diagnostics import RemoteSystemContext


class UbuntuAIApp(VoiceControllerMixin, FirstRunControllerMixin, PanelControllerMixin):
    """Interface desktop do Ubuntu AI Assistant."""

    def __init__(self) -> None:
        self._backend = GUIBackend()
        self._busy = False
        self._operation_generation = 0
        self._operation_started_at: dict[int, float] = {}
        self._active_actions: tk.Frame | None = None
        self._active_plan_card: tk.Frame | None = None
        self._care_panel: tk.Frame | None = None
        self._resources_panel: tk.Frame | None = None
        self._resources_listbox: tk.Listbox | None = None
        self._resources_detail_label: tk.Label | None = None
        self._resource_hover_after_id: str | None = None
        self._resource_hover_index: int | None = None
        self._resource_topics = ()
        self._automation_panel: tk.Frame | None = None
        self._automation_listbox: tk.Listbox | None = None
        self._automation_summary_label: tk.Label | None = None
        self._automation_tasks = ()
        self._active_automation_task_id: str | None = None
        self._ui_queue = SimpleQueue()

        self.root = tk.Tk(className=WINDOW_CLASS)
        self.root.title("Ubuntu AI Assistant")
        self.root.geometry("1040x760")
        self.root.minsize(780, 580)
        self.root.configure(bg=BACKGROUND)
        self.root.after(25, self._drain_ui_queue)
        self._set_window_icon()

        self._build_interface()
        self._refresh_remote_targets()
        self._bind_accessibility_shortcuts()
        self._bind_mousewheel()
        self.root.bind(
            "<Unmap>",
            self._hide_capabilities_panel,
            add="+",
        )
        self.root.bind("<Unmap>", self._hide_automation_panel, add="+")
        self.root.bind("<Unmap>", self._hide_care_panel, add="+")
        self.root.bind(
            "<Escape>",
            self._hide_capabilities_panel,
            add="+",
        )
        self.root.bind("<Escape>", self._hide_automation_panel, add="+")
        self.root.bind("<Escape>", self._hide_care_panel, add="+")
        self.root.bind(
            "<Button-1>",
            self._close_capabilities_on_outside_click,
            add="+",
        )
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
        widgets = build_main_interface(
            self.root,
            window_icon=self._window_icon,
            on_show_capabilities=self._show_capabilities,
            on_show_care=self._show_care_panel,
            on_show_automation=self._show_automation_panel,
            on_toggle_remote=self._toggle_remote_controls,
            on_target_selected=self._on_target_selected,
            on_add_remote=self._add_remote_host,
            on_remove_remote=self._remove_remote_host,
            on_diagnose_remote=self._start_remote_diagnostics,
            on_resize_messages=self._resize_messages,
            on_enter=self._on_enter,
            on_voice=self._start_voice_input,
            on_submit=self.submit,
        )

        self._header_icon = widgets.header_icon
        self.status_label = widgets.status_label
        self.care_button = widgets.care_button
        self.resources_button = widgets.resources_button
        self.automation_button = widgets.automation_button
        self._remote_controls_visible = False
        self.remote_controls_button = widgets.remote_controls_button
        self.remote_controls = widgets.remote_controls
        self.target_variable = widgets.target_variable
        self.target_menu = widgets.target_menu
        self.content = widgets.content
        self.canvas = widgets.canvas
        self.scrollbar = widgets.scrollbar
        self.messages = widgets.messages
        self.canvas_window = widgets.canvas_window
        self.composer_outer = widgets.composer_outer
        self.composer = widgets.composer
        self.request_entry = widgets.request_entry
        self.voice_button = widgets.voice_button
        self.send_button = widgets.send_button
        bind_hover_reveal(
            self.remote_controls_button,
            foreground=lambda: WARNING if self._backend.is_remote_selected else TEXT,
            visible_background=SURFACE_ALT,
        )
        bind_hover_reveal(self.automation_button, foreground=TEXT_MUTED)
        bind_hover_reveal(self.resources_button, foreground=TEXT_MUTED)
        bind_hover_reveal(self.care_button, foreground=TEXT_MUTED)

    def _bind_mousewheel(self) -> None:
        """Habilita roda do mouse e touchpad no histórico da conversa."""

        self.root.bind_all("<MouseWheel>", self._on_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self._on_mousewheel, add="+")
        self.root.bind_all("<Button-5>", self._on_mousewheel, add="+")

    def _on_mousewheel(self, event: tk.Event) -> str:
        units = self._mousewheel_units(
            delta=getattr(event, "delta", 0),
            button=getattr(event, "num", 0),
        )
        if units:
            self.canvas.yview_scroll(units, "units")
        return "break"

    @staticmethod
    def _mousewheel_units(*, delta: int, button: int) -> int:
        if button == 4:
            return -3
        if button == 5:
            return 3
        if delta == 0:
            return 0
        steps = max(1, abs(delta) // 120)
        return -steps if delta > 0 else steps

    def _refresh_remote_targets(self) -> None:
        names = ("local", *(host.name for host in self._backend.remote_hosts()))
        menu = self.target_menu["menu"]
        menu.delete(0, tk.END)
        for name in names:
            menu.add_command(
                label=name,
                command=lambda selected=name: self._select_target(selected),
            )
        if self.target_variable.get() not in names:
            self._select_target("local")

    def _select_target(self, name: str) -> None:
        host = self._backend.select_target(name)
        self.target_variable.set(host.name)
        remote = host.name.lower() != "local"
        self.target_menu.configure(fg=WARNING if remote else TEXT)
        self.remote_controls_button.configure(
            text=self._remote_button_text(
                host.name,
                expanded=self._remote_controls_visible,
            ),
        )
        self.status_label.configure(
            text=f"●  {'Remoto: ' + host.name if remote else 'Pronto'}",
            fg=WARNING if remote else SUCCESS,
        )

    @staticmethod
    def _remote_button_text(target: str, *, expanded: bool) -> str:
        return remote_button_text(target, expanded=expanded)

    def _toggle_remote_controls(self) -> None:
        self._hide_capabilities_panel()
        self._hide_automation_panel()
        self._hide_care_panel()
        if self._remote_controls_visible:
            self._hide_remote_controls()
            return

        self._remote_controls_visible = True
        place_remote_controls(self.remote_controls, self.remote_controls_button, self.root)
        self.remote_controls_button.configure(
            text=self._remote_button_text(
                self.target_variable.get(),
                expanded=True,
            )
        )

    def _hide_remote_controls(self) -> None:
        if not self._remote_controls_visible:
            return

        self._remote_controls_visible = False
        self.remote_controls.place_forget()
        self.remote_controls_button.configure(
            text=self._remote_button_text(
                self.target_variable.get(),
                expanded=False,
            )
        )

    def _on_target_selected(self, name: str) -> None:
        try:
            self._select_target(name)
        except (KeyError, ValueError) as exc:
            messagebox.showerror("Destino inválido", str(exc), parent=self.root)
            self._select_target("local")

    def _add_remote_host(self) -> None:
        name = simpledialog.askstring("Novo host", "Nome do destino:", parent=self.root)
        if not name:
            return
        hostname = simpledialog.askstring("Novo host", "Hostname ou IP:", parent=self.root)
        if not hostname:
            return
        user = simpledialog.askstring("Novo host", "Usuário SSH (opcional):", parent=self.root)
        port_text = simpledialog.askstring(
            "Novo host", "Porta SSH:", initialvalue="22", parent=self.root
        )
        identity = simpledialog.askstring(
            "Novo host", "Caminho absoluto da chave (opcional):", parent=self.root
        )
        known_hosts = simpledialog.askstring(
            "Novo host", "Caminho absoluto de known_hosts (opcional):", parent=self.root
        )
        try:
            host = self._backend.register_remote_host(
                name=name,
                hostname=hostname,
                user=user or None,
                port=int(port_text or "22"),
                identity_file=identity or None,
                known_hosts_file=known_hosts or None,
            )
        except (TypeError, ValueError) as exc:
            messagebox.showerror("Host não cadastrado", str(exc), parent=self.root)
            return
        self._refresh_remote_targets()
        self._select_target(host.name)

    def _remove_remote_host(self) -> None:
        name = self.target_variable.get()
        if name == "local":
            messagebox.showinfo(
                "Destino local", "O computador local não pode ser removido.", parent=self.root
            )
            return
        if not messagebox.askyesno("Remover host", f"Remover o destino {name}?", parent=self.root):
            return
        self._backend.remove_remote_host(name)
        self._refresh_remote_targets()

    def _start_remote_diagnostics(self) -> None:
        if not self._backend.is_remote_selected:
            messagebox.showinfo(
                "Destino remoto", "Selecione primeiro um computador remoto.", parent=self.root
            )
            return
        operation = self._begin_operation("Conectando")
        threading.Thread(
            target=self._collect_remote_diagnostics,
            args=(operation,),
            daemon=True,
        ).start()

    def _post_to_ui(self, callback, *args) -> None:
        """Entrega resultados de workers sem chamar o Tkinter fora da thread principal."""

        self._ui_queue.put((callback, args))

    def _drain_ui_queue(self) -> None:
        """Executa, na thread principal, os eventos publicados pelos workers."""

        try:
            while True:
                callback, args = self._ui_queue.get_nowait()
                callback(*args)
        except Empty:
            pass
        finally:
            try:
                self.root.after(25, self._drain_ui_queue)
            except tk.TclError:
                pass

    def _collect_remote_diagnostics(self, operation: int) -> None:
        try:
            health = self._backend.test_remote_connection()
            if not health.healthy:
                raise ConnectionError(health.message)
            context = self._backend.remote_diagnostics()
        except Exception as exc:
            self._post_to_ui(self._deliver_error, operation, str(exc))
            return
        self._post_to_ui(self._deliver_remote_diagnostics, operation, context)

    def _deliver_remote_diagnostics(
        self,
        operation: int,
        context: RemoteSystemContext,
    ) -> None:
        if operation != self._operation_generation:
            return
        self._set_busy(False)
        lines = [f"Diagnóstico remoto · {context.host_name}"]
        for item in context.items:
            status = "OK" if item.success else "FALHA"
            lines.append(f"\n[{status}] {item.name}\n{item.output or 'Sem saída.'}")
        self._add_system_message("\n".join(lines), color=TEXT)

    def _show_welcome(self) -> None:
        widgets = build_welcome(
            self.messages,
            window_icon=self._window_icon,
        )
        self.welcome = widgets.frame
        self._welcome_icon = widgets.icon
        self._check_ai_setup()

    # ------------------------------------------------------------------
    # Request
    # ------------------------------------------------------------------

    def submit(
        self,
        request_override: str | None = None,
        display_request: str | None = None,
    ) -> None:
        if self._busy:
            return

        request = (
            request_override.strip()
            if request_override is not None
            else self.request_entry.get().strip()
        )
        if not request:
            return
        self.request_entry.delete(0, tk.END)

        if self.welcome.winfo_exists():
            self.welcome.destroy()
            self.composer_outer.pack_configure(pady=(0, 24))

        self._add_user_message(display_request or request)
        confirm_pending = self._backend.is_confirm_pending_request(request)
        cancel_pending = self._backend.is_cancel_pending_request(request)
        if request_override is not None and confirm_pending:
            self._add_system_message(
                "Confirmações por voz não são aceitas. Use o botão do plano para autorizar.",
                color=WARNING,
            )
            return
        if confirm_pending or cancel_pending:
            if not self._backend.has_pending_plan():
                action = "confirmar" if confirm_pending else "cancelar"
                self._add_system_message(f"Não há plano pendente para {action}.", color=WARNING)
            elif confirm_pending:
                self.confirm()
            else:
                self.cancel()
            return
        if self._backend.is_remote_diagnostic_request(request):
            self._start_remote_diagnostics()
            return

        if self._backend.is_cancel_selected_automation_request(request):
            self._automation_action("cancel")
            return

        multi_agent_request = self._multi_agent_request(request)
        if multi_agent_request is not None:
            self._show_multi_agent_plan(multi_agent_request)
            return

        if self._backend.is_remote_selected and self._backend.is_system_fact_request(request):
            target = self._backend.selected_target
            operation = self._begin_operation(f"Consultando {target}")
            threading.Thread(
                target=self._start_selected_system_fact,
                args=(request, target, operation),
                daemon=True,
            ).start()
            return

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

        if self._backend.is_remote_selected:
            self._add_system_message(
                "Destino remoto selecionado. Por segurança, use Diagnosticar para "
                "consultas remotas nesta etapa. A solicitação não foi executada localmente.",
                color=WARNING,
            )
            self.request_entry.focus_set()
            return

        if self._backend.has_pending_plan():
            self._add_system_message(
                "Já existe um plano aguardando sua decisão. Use o card ou diga "
                "'Confirme o plano pendente' / 'Cancele o plano pendente'.",
                color=WARNING,
            )
            self.request_entry.focus_set()
            return
        operation = self._begin_operation("Analisando")
        self._operation_started_at[operation] = perf_counter()

        threading.Thread(
            target=self._start_request,
            args=(request, operation),
            daemon=True,
        ).start()

    def _show_capabilities(self) -> None:
        self._hide_automation_panel()
        self._hide_care_panel()
        panel = getattr(self, "_resources_panel", None)
        if panel is not None and panel.winfo_ismapped():
            self._hide_capabilities_panel()
            return

        topics = self._backend.capability_topics()
        self._resource_topics = topics
        if not topics:
            return

        if panel is None or not panel.winfo_exists():
            panel = self._build_capabilities_panel()
            self._resources_panel = panel

        listbox = self._resources_listbox
        if listbox is None:
            return

        listbox.delete(0, tk.END)
        for topic in topics:
            listbox.insert(tk.END, f"{topic.code}. {topic.title}")

        self.root.update_idletasks()
        button_right = (
            self.resources_button.winfo_rootx()
            - self.root.winfo_rootx()
            + self.resources_button.winfo_width()
        )
        button_bottom = (
            self.resources_button.winfo_rooty()
            - self.root.winfo_rooty()
            + self.resources_button.winfo_height()
        )

        panel.place(
            x=button_right,
            y=button_bottom + 6,
            width=480,
            anchor=tk.NE,
        )
        panel.lift()

        self.resources_button.configure(text="Recursos e ajuda  ▴")
        self._display_capability_detail(0)
        listbox.focus_set()

    def _build_capabilities_panel(self) -> tk.Frame:
        widgets = build_capabilities_panel(
            self.root,
            on_close=self._hide_capabilities_panel,
            on_motion=self._schedule_capability_detail,
            on_leave=self._cancel_capability_detail,
            on_activate=self._activate_capability,
        )
        self._resources_listbox = widgets.listbox
        self._resources_detail_label = widgets.detail
        return widgets.panel

    def _schedule_capability_detail(self, event: tk.Event) -> None:
        listbox = self._resources_listbox
        if listbox is None or not self._resource_topics:
            return

        index = listbox.nearest(event.y)
        bounds = listbox.bbox(index)
        if bounds is None or event.y > bounds[1] + bounds[3]:
            self._cancel_capability_detail()
            return

        if index == self._resource_hover_index:
            return

        self._cancel_capability_detail()
        self._resource_hover_index = index
        self._resource_hover_after_id = self.root.after(
            140,
            lambda selected=index: self._display_capability_detail(selected),
        )

    def _cancel_capability_detail(self, _event: tk.Event | None = None) -> None:
        after_id = getattr(self, "_resource_hover_after_id", None)
        if after_id is not None:
            try:
                self.root.after_cancel(after_id)
            except tk.TclError:
                pass

        self._resource_hover_after_id = None
        self._resource_hover_index = None

    def _display_capability_detail(self, index: int) -> None:
        self._resource_hover_after_id = None
        if index >= len(self._resource_topics):
            return

        listbox = self._resources_listbox
        detail = self._resources_detail_label
        if listbox is None or detail is None:
            return

        topic = self._resource_topics[index]
        summary = (
            f"{topic.title}\n\n"
            f"• {topic.capabilities[0]}\n"
            f"Exemplo: {topic.examples[0]}\n\n"
            f"Risco: {topic.risk} · Disponibilidade: {topic.availability}"
        )

        listbox.selection_clear(0, tk.END)
        listbox.selection_set(index)
        listbox.activate(index)
        listbox.see(index)
        detail.configure(text=summary)

    def _activate_capability(self, event: tk.Event | None = None) -> str:
        listbox = self._resources_listbox
        if listbox is None:
            return "break"

        if event is not None and getattr(event, "y", None) is not None:
            index = listbox.nearest(event.y)
        else:
            selected = listbox.curselection()
            if not selected:
                return "break"
            index = selected[0]

        if index >= len(self._resource_topics):
            return "break"

        code = self._resource_topics[index].code
        self._hide_capabilities_panel()
        self._send_resource_to_conversation(code)
        return "break"

    def _hide_capabilities_panel(self, _event: tk.Event | None = None) -> None:
        self._cancel_capability_detail()

        panel = getattr(self, "_resources_panel", None)
        if panel is not None and panel.winfo_exists():
            panel.place_forget()

        button = getattr(self, "resources_button", None)
        if button is not None and button.winfo_exists():
            button.configure(text="Recursos e ajuda  ▾")

    @staticmethod
    def _multi_agent_request(request: str) -> str | None:
        normalized = request.strip()
        lowered = normalized.lower().rstrip("?.!")

        natural_requests = {
            "analise este problema de rede": "problema de rede",
            "diagnostique a falta de espaço": "falta de espaço",
            "investigue meu problema de conexão": "problema de rede",
            "analise por que o disco está cheio": "falta de espaço",
        }
        if lowered in natural_requests:
            return natural_requests[lowered]

        for prefix in ("agentes:", "multiagente:"):
            if lowered.startswith(prefix):
                return normalized[len(prefix) :].strip()
        return None

    def _show_multi_agent_plan(self, request: str) -> None:
        try:
            goal = self._backend.plan_multi_agent(
                request,
                goal_id=f"gui-{int(perf_counter() * 1_000_000)}",
            )
        except ValueError as exc:
            self._add_system_message(str(exc), color=WARNING)
            self.request_entry.focus_set()
            return

        target = goal.context["target"]
        lines = [
            f"Plano multiagente · {target}",
            f"Objetivo: {goal.description}",
            "",
        ]
        for task in goal.tasks:
            command = " ".join(task.payload.actions[0].argv)
            lines.append(f"• {task.specialist.value}: {command} (somente leitura)")
        lines.extend(
            (
                "",
                "Prévia criada sem executar comandos. Confirmação e política de risco ",
                "continuam centralizadas antes de qualquer execução.",
            )
        )
        self._add_system_message("\n".join(lines), color=TEXT)
        confirmed = messagebox.askyesno(
            "Executar diagnóstico multiagente",
            "Executar agora os comandos de consulta exibidos?\n\n"
            "Eles são somente leitura e usarão o computador selecionado. Você poderá "
            "acompanhar, pausar ou cancelar pelo painel Agentes e progresso.",
            parent=self.root,
        )
        if not confirmed:
            self._add_system_message(
                "Prévia mantida sem execução. Nenhum comando foi iniciado.",
                color=TEXT_MUTED,
            )
            self.request_entry.focus_set()
            return

        try:
            task = self._backend.register_multi_agent(goal)
        except ValueError as exc:
            self._add_system_message(str(exc), color=WARNING)
            self.request_entry.focus_set()
            return
        self._active_automation_task_id = task.task_id
        operation = self._begin_operation("Executando agentes")
        self._poll_automation_panel(operation)
        threading.Thread(
            target=self._start_multi_agent_execution,
            args=(goal, operation),
            daemon=True,
        ).start()

    def _start_multi_agent_execution(self, goal: object, operation: int) -> None:
        try:
            report = self._backend.execute_multi_agent(goal, confirmed=True)
        except Exception as exc:
            self._post_to_ui(self._deliver_error, operation, str(exc))
            return
        self._post_to_ui(self._deliver_multi_agent_report, operation, report)

    def _poll_automation_panel(self, operation: int) -> None:
        if operation != self._operation_generation or not self._busy:
            return
        self._refresh_automation_panel()
        self.root.after(350, self._poll_automation_panel, operation)

    def _deliver_multi_agent_report(
        self,
        operation: int,
        report: MultiAgentExecutionReport,
    ) -> None:
        if operation != self._operation_generation:
            return
        self._active_automation_task_id = None
        self._set_busy(False)
        self._refresh_automation_panel()
        self._hide_automation_panel()
        if report.cancelled:
            self._add_system_message(
                "Diagnóstico multiagente cancelado pelo usuário.",
                color=WARNING,
            )
            return

        lines = [f"Resultado multiagente · {report.target}", ""]
        for result in report.results:
            command = " ".join(result.command)
            output = (result.stdout or result.stderr or "Sem saída.").strip()
            if len(output) > 3000:
                output = output[:3000] + "\n… saída resumida"
            status = "OK" if result.success else "FALHA"
            lines.append(f"[{status}] $ {command}\n{output}\n")
        lines.append(
            "Diagnóstico concluído e registrado na auditoria. "
            "Nenhum comando de alteração foi executado."
        )
        self._add_system_message(
            "\n".join(lines),
            color=TEXT if report.successful else WARNING,
        )
        self.request_entry.focus_set()

    def _show_automation_panel(self) -> None:
        self._hide_capabilities_panel()
        self._hide_care_panel()
        panel = getattr(self, "_automation_panel", None)
        if panel is not None and panel.winfo_ismapped():
            self._hide_automation_panel()
            return
        if panel is None or not panel.winfo_exists():
            panel = self._build_automation_panel()
            self._automation_panel = panel

        self._refresh_automation_panel()
        self.root.update_idletasks()
        button_right = (
            self.automation_button.winfo_rootx()
            - self.root.winfo_rootx()
            + self.automation_button.winfo_width()
        )
        button_bottom = (
            self.automation_button.winfo_rooty()
            - self.root.winfo_rooty()
            + self.automation_button.winfo_height()
        )
        panel.place(x=button_right, y=button_bottom + 6, width=540, anchor=tk.NE)
        panel.lift()
        self.automation_button.configure(text="Agentes e progresso  ▴")

    def _build_automation_panel(self) -> tk.Frame:
        widgets = build_automation_panel(
            self.root,
            on_close=self._hide_automation_panel,
            on_action=self._automation_action,
        )
        self._automation_listbox = widgets.tasks
        self._automation_summary_label = widgets.summary
        return widgets.panel

    def _refresh_automation_panel(self) -> None:
        tasks = self._backend.automation_tasks()
        metrics = self._backend.automation_metrics()
        events = self._backend.automation_events()
        self._automation_tasks = tasks
        listbox = self._automation_listbox
        summary = self._automation_summary_label
        if listbox is None or summary is None:
            return
        listbox.delete(0, tk.END)
        for task in tasks:
            listbox.insert(tk.END, task_row(task))
        if not tasks:
            listbox.insert(tk.END, "Nenhuma tarefa automatizada registrada.")
        summary.configure(
            text=summary_text(
                target=self._backend.selected_target,
                metrics=metrics,
                event_count=len(events),
            )
        )

    def _automation_action(self, action: str) -> None:
        if action == "refresh":
            self._refresh_automation_panel()
            return
        listbox = self._automation_listbox
        if listbox is None or not listbox.curselection() or not self._automation_tasks:
            messagebox.showinfo(
                "Tarefa necessária",
                "Selecione uma tarefa para aplicar o controle.",
                parent=self.root,
            )
            return
        task = self._automation_tasks[listbox.curselection()[0]]
        handlers = {
            "pause": self._backend.pause_automation,
            "resume": self._backend.resume_automation,
            "cancel": self._backend.cancel_automation,
        }
        try:
            handlers[action](task.task_id)
        except (KeyError, ValueError) as exc:
            messagebox.showerror("Controle não aplicado", str(exc), parent=self.root)
        self._refresh_automation_panel()

    def _hide_automation_panel(self, _event: tk.Event | None = None) -> None:
        panel = getattr(self, "_automation_panel", None)
        if panel is not None and panel.winfo_exists():
            panel.place_forget()
        button = getattr(self, "automation_button", None)
        if button is not None and button.winfo_exists():
            button.configure(text="Agentes e progresso  ▾")

    def _send_resource_to_conversation(self, code: str) -> None:
        self._hide_capabilities_panel()
        detail = self._backend.capability_detail(code)
        self._add_system_message(f"{detail}\n\nRota local · recursos", color=TEXT)
        self.request_entry.focus_set()

    def _start_selected_system_fact(
        self,
        request: str,
        target: str,
        operation: int,
    ) -> None:
        try:
            response = self._backend.selected_system_fact(
                request,
                target_name=target,
            )
        except Exception as exc:
            self._post_to_ui(self._deliver_error, operation, str(exc))
            return

        self._post_to_ui(
            self._deliver_selected_system_fact,
            operation,
            response,
            target,
        )

    def _deliver_selected_system_fact(
        self,
        operation: int,
        response: str,
        target: str,
    ) -> None:
        if operation != self._operation_generation:
            return

        self._set_busy(False)
        self._add_system_message(
            f"{response}\n\nRota SSH somente leitura · {target}",
            color=TEXT,
        )
        self.request_entry.focus_set()

    def _start_request(
        self,
        request: str,
        operation: int,
    ) -> None:
        try:
            snapshot = self._backend.start(request)
        except Exception as exc:
            self._post_to_ui(
                self._deliver_error,
                operation,
                str(exc),
            )
            return

        self._post_to_ui(
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
            self._post_to_ui(self._deliver_error, operation, str(exc))
            return

        self._post_to_ui(self._deliver_chat, operation, response)

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
        add_user_message(self.messages, message=message)
        self._scroll_bottom()

    def _add_system_message(
        self,
        message: str,
        *,
        color: str = TEXT,
    ) -> None:
        add_system_message(
            self.messages,
            message=message,
            color=color,
        )
        self._scroll_bottom()

    # ------------------------------------------------------------------
    # Plan
    # ------------------------------------------------------------------

    def _add_plan_card(self, snapshot: LoopSnapshot, plan: object) -> None:
        widgets = build_plan_card(
            self.messages,
            snapshot=snapshot,
            plan=plan,
            on_confirm=self.confirm,
            on_cancel=self.cancel,
        )
        self._active_plan_card = widgets.outer
        self._active_actions = widgets.actions
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
            self._post_to_ui(
                self._deliver_error,
                operation,
                str(exc),
            )
            return

        self._post_to_ui(
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

    def _add_execution_result(self, result: object) -> None:
        build_execution_result_card(self.messages, result=result)
        self._scroll_bottom()

    # ------------------------------------------------------------------
    # Cancel / errors
    # ------------------------------------------------------------------

    def cancel_current_operation(self) -> None:
        if not self._busy:
            return

        self._operation_generation += 1
        getattr(self, "_operation_started_at", {}).clear()

        automation_task_id = getattr(self, "_active_automation_task_id", None)
        if automation_task_id is not None:
            try:
                self._backend.cancel_automation(automation_task_id)
            except (KeyError, ValueError):
                pass
            self._active_automation_task_id = None

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
        return friendly_error(message)

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
            font=FONT_TINY,
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
        return format_duration(duration)

    def _set_busy(
        self,
        busy: bool,
        label: str = "Pronto",
    ) -> None:
        self._busy = busy
        apply_busy_state(
            busy=busy,
            label=label,
            status_label=self.status_label,
            send_button=self.send_button,
            request_entry=self.request_entry,
            on_submit=self.submit,
            on_cancel=self.cancel_current_operation,
        )

    @staticmethod
    def _command_text(command: object) -> str:
        return command_text(command)

    @staticmethod
    def _state_message(snapshot: LoopSnapshot) -> str:
        return state_message(snapshot)

    @staticmethod
    def _risk_label(risk: str) -> str:
        return risk_label(risk)

    @staticmethod
    def _risk_color(risk: str) -> str:
        return risk_color(
            risk,
            success=SUCCESS,
            warning=WARNING,
            error=ERROR,
        )

    def _resize_messages(
        self,
        event: tk.Event,
    ) -> None:
        self.canvas.itemconfigure(
            self.canvas_window,
            width=event.width,
        )

    def _scroll_bottom(self) -> None:
        scroll_canvas_bottom(self.root, self.canvas)

    def _bind_accessibility_shortcuts(self) -> None:
        self.root.bind("<Escape>", self._on_escape)
        self.root.bind("<Control-l>", self._focus_request)
        self.root.bind("<Control-L>", self._focus_request)

    def _on_escape(
        self,
        _event: tk.Event | None = None,
    ) -> str:
        self._hide_capabilities_panel()
        self._hide_automation_panel()
        self._hide_remote_controls()
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

    def request_activation(self) -> None:
        """Agenda a restauração da janela a partir do listener de instância única."""

        self._post_to_ui(self._activate_window)

    def _activate_window(self) -> None:
        """Restaura, eleva e focaliza a janela já aberta."""

        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(150, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()


def main() -> None:
    instance = SingleInstance()
    if not instance.acquire_or_activate():
        return

    try:
        application = UbuntuAIApp()
        instance.start(application.request_activation)
        application.run()
    finally:
        instance.close()


if __name__ == "__main__":
    main()
