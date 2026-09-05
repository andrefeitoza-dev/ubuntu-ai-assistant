from __future__ import annotations

import threading
import tkinter as tk
import webbrowser
from queue import Empty, SimpleQueue

from ubuntu_ai.distribution.first_run import OLLAMA_INSTALL_URL, FirstRunSetup, FirstRunStatus
from ubuntu_ai.gui.theme import (
    ACCENT,
    BACKGROUND,
    ERROR,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
    FONT_TITLE,
    SUCCESS,
    SURFACE_ALT,
    TEXT,
    TEXT_MUTED,
    WARNING,
    WINDOW_CLASS,
)
from ubuntu_ai.voice import (
    NaturalVoiceSetup,
    VoiceInputService,
    VoiceModelSetup,
    VoiceOutputService,
    VoiceSetupStatus,
)


def setup_message(status: FirstRunStatus) -> tuple[str, str]:
    if not status.ollama_available:
        return (
            "1 de 3 · Instale o Ollama",
            "O Ollama não foi encontrado. Abra as instruções oficiais, conclua a instalação "
            "e volte para verificar novamente.",
        )
    if not status.ollama_running:
        return (
            "2 de 3 · Inicie o Ollama",
            "O Ollama está instalado, mas o serviço não respondeu. Inicie o serviço e "
            "verifique novamente.",
        )
    if not status.model_available:
        return (
            "3 de 3 · Baixe o modelo local",
            f"O modelo {status.model} ainda não está disponível. O download pode ocupar "
            "alguns gigabytes e só começa quando você autorizar.",
        )
    return (
        "Configuração concluída",
        f"Ollama e o modelo {status.model} estão disponíveis. O assistente está pronto.",
    )


class SetupApp:
    """Assistente gráfico, explícito e não privilegiado para o runtime local."""

    def __init__(self, setup: FirstRunSetup | None = None) -> None:
        self._setup = setup or FirstRunSetup()
        self._voice_setup = VoiceModelSetup()
        self._natural_voice_setup = NaturalVoiceSetup()
        self._queue: SimpleQueue[tuple[str, object]] = SimpleQueue()
        self.root = tk.Tk(className=WINDOW_CLASS)
        self.root.title("Configurar Ubuntu AI Assistant")
        self.root.geometry("640x650")
        self.root.minsize(580, 600)
        self.root.configure(bg=BACKGROUND)
        self._build()
        self.root.after(50, self._drain_queue)
        self._display_voice_status(self._voice_setup.status())
        self._display_natural_voice_status()
        self.refresh()

    def _build(self) -> None:
        content = tk.Frame(self.root, bg=BACKGROUND, padx=34, pady=24)
        content.pack(fill=tk.BOTH, expand=True)
        tk.Label(
            content,
            text="Configurar IA local",
            bg=BACKGROUND,
            fg=TEXT,
            font=FONT_TITLE,
        ).pack(anchor="w")
        tk.Label(
            content,
            text="O aplicativo básico já está instalado. Estas etapas opcionais habilitam "
            "conversas e planejamento com IA no próprio computador.",
            bg=BACKGROUND,
            fg=TEXT_MUTED,
            font=FONT_BODY,
            justify=tk.LEFT,
            wraplength=520,
        ).pack(anchor="w", pady=(8, 16))
        card = tk.Frame(content, bg=SURFACE_ALT, padx=20, pady=16)
        card.pack(fill=tk.X)
        self.title_label = tk.Label(card, bg=SURFACE_ALT, fg=TEXT, font=FONT_BODY_BOLD, anchor="w")
        self.title_label.pack(fill=tk.X)
        self.detail_label = tk.Label(
            card,
            bg=SURFACE_ALT,
            fg=TEXT_MUTED,
            font=FONT_BODY,
            justify=tk.LEFT,
            wraplength=470,
            anchor="w",
        )
        self.detail_label.pack(fill=tk.X, pady=(8, 12))
        self.progress = tk.Label(card, text="", bg=SURFACE_ALT, fg=WARNING, font=FONT_SMALL)
        self.progress.pack(anchor="w")
        actions = tk.Frame(card, bg=SURFACE_ALT)
        actions.pack(fill=tk.X, pady=(12, 0))
        self.primary = tk.Button(
            actions,
            text="Verificar novamente",
            command=self.refresh,
            bg=ACCENT,
            fg="#101318",
            relief=tk.FLAT,
            padx=14,
            pady=8,
            font=FONT_SMALL,
            cursor="hand2",
        )
        self.primary.pack(side=tk.LEFT)
        tk.Button(
            actions,
            text="Fechar",
            command=self.root.destroy,
            bg=SURFACE_ALT,
            fg=TEXT_MUTED,
            relief=tk.FLAT,
            padx=14,
            pady=8,
            font=FONT_SMALL,
            cursor="hand2",
        ).pack(side=tk.RIGHT)

        voice_card = tk.Frame(content, bg=SURFACE_ALT, padx=20, pady=16)
        voice_card.pack(fill=tk.X, pady=(14, 0))
        self.voice_title = tk.Label(
            voice_card,
            text="Comandos por voz",
            bg=SURFACE_ALT,
            fg=TEXT,
            font=FONT_BODY_BOLD,
            anchor="w",
        )
        self.voice_title.pack(fill=tk.X)
        self.voice_detail = tk.Label(
            voice_card,
            bg=SURFACE_ALT,
            fg=TEXT_MUTED,
            font=FONT_BODY,
            justify=tk.LEFT,
            wraplength=470,
            anchor="w",
        )
        self.voice_detail.pack(fill=tk.X, pady=(10, 14))
        self.voice_button = tk.Button(
            voice_card,
            text="Baixar modelo de voz (31 MB)",
            command=self._download_voice_model,
            bg=ACCENT,
            fg="#101318",
            relief=tk.FLAT,
            padx=14,
            pady=8,
            font=FONT_SMALL,
            cursor="hand2",
        )
        self.voice_button.pack(anchor="w")

        output_card = tk.Frame(content, bg=SURFACE_ALT, padx=20, pady=16)
        output_card.pack(fill=tk.X, pady=(14, 0))
        tk.Label(
            output_card,
            text="Voz natural do assistente",
            bg=SURFACE_ALT,
            fg=TEXT,
            font=FONT_BODY_BOLD,
            anchor="w",
        ).pack(fill=tk.X)
        self.natural_voice_detail = tk.Label(
            output_card,
            bg=SURFACE_ALT,
            fg=TEXT_MUTED,
            font=FONT_BODY,
            justify=tk.LEFT,
            wraplength=470,
            anchor="w",
        )
        self.natural_voice_detail.pack(fill=tk.X, pady=(10, 14))
        self.natural_voice_button = tk.Button(
            output_card,
            text="Baixar voz natural (58 MB)",
            command=self._download_natural_voice,
            bg=ACCENT,
            fg="#101318",
            relief=tk.FLAT,
            padx=14,
            pady=8,
            font=FONT_SMALL,
            cursor="hand2",
        )
        self.natural_voice_button.pack(anchor="w")

    def refresh(self) -> None:
        self._set_busy(True, "Verificando configuração…")
        threading.Thread(target=self._check_worker, daemon=True).start()

    def _check_worker(self) -> None:
        try:
            self._queue.put(("status", self._setup.status()))
        except Exception as exc:
            self._queue.put(("error", str(exc)))

    def _display_status(self, status: FirstRunStatus) -> None:
        title, detail = setup_message(status)
        self.title_label.configure(text=title)
        self.detail_label.configure(text=detail)
        self.progress.configure(text="", fg=SUCCESS if status.ready else WARNING)
        self.primary.configure(state=tk.NORMAL)
        if not status.ollama_available:
            self.primary.configure(
                text="Abrir instruções oficiais",
                command=self._open_instructions,
            )
        elif status.ollama_running and not status.model_available:
            self.primary.configure(text=f"Baixar {status.model}", command=self._download_model)
        elif status.ready:
            self.primary.configure(text="Verificar novamente", command=self.refresh)
        else:
            self.primary.configure(text="Verificar novamente", command=self.refresh)

    def _open_instructions(self) -> None:
        webbrowser.open(OLLAMA_INSTALL_URL)

    def _download_model(self) -> None:
        self._set_busy(True, "Baixando o modelo local… não feche esta janela.")
        threading.Thread(target=self._download_worker, daemon=True).start()

    def _download_worker(self) -> None:
        try:
            result = self._setup.pull_model()
            if result.returncode:
                self._queue.put(("error", result.stderr.strip() or "Download não concluído."))
            else:
                self._queue.put(("status", self._setup.status()))
        except Exception as exc:
            self._queue.put(("error", str(exc)))

    def _display_voice_status(self, status: VoiceSetupStatus) -> None:
        if not status.model_available:
            self.voice_detail.configure(
                text="O reconhecimento é local. O modelo português oficial é separado e "
                "só será baixado após sua autorização."
            )
            self.voice_button.configure(state=tk.NORMAL, text="Baixar modelo de voz (31 MB)")
            return
        availability = VoiceInputService(model_path=status.model_path).availability()
        self.voice_detail.configure(text=availability.message)
        self.voice_button.configure(
            state=tk.DISABLED if availability.available else tk.NORMAL,
            text="Voz pronta" if availability.available else "Verificar suporte de voz",
            command=(lambda: self._display_voice_status(self._voice_setup.status())),
        )

    def _download_voice_model(self) -> None:
        self.voice_button.configure(state=tk.DISABLED, text="Baixando e verificando…")
        self.voice_detail.configure(
            text="Baixando por HTTPS e validando a integridade antes da instalação."
        )
        threading.Thread(target=self._voice_download_worker, daemon=True).start()

    def _voice_download_worker(self) -> None:
        try:
            self._voice_setup.install()
            self._queue.put(("voice-status", self._voice_setup.status()))
        except Exception as exc:
            self._queue.put(("voice-error", str(exc)))

    def _display_natural_voice_status(self) -> None:
        available = self._natural_voice_setup.available()
        service = VoiceOutputService(model_path=self._natural_voice_setup.model_path)
        ready = available and service.neural_available
        self.natural_voice_detail.configure(
            text=(
                "Voz neural brasileira instalada e pronta para uso local."
                if ready
                else "Baixe a voz neural brasileira. Ela funciona localmente e soa mais natural."
            ),
            fg=SUCCESS if ready else TEXT_MUTED,
        )
        self.natural_voice_button.configure(
            state=tk.DISABLED if ready else tk.NORMAL,
            text="Voz natural pronta" if ready else "Baixar voz natural (58 MB)",
        )

    def _download_natural_voice(self) -> None:
        self.natural_voice_button.configure(state=tk.DISABLED, text="Baixando e verificando…")
        threading.Thread(target=self._natural_voice_download_worker, daemon=True).start()

    def _natural_voice_download_worker(self) -> None:
        try:
            self._natural_voice_setup.install()
            self._queue.put(("natural-voice-status", True))
        except Exception as exc:
            self._queue.put(("natural-voice-error", str(exc)))

    def _set_busy(self, busy: bool, message: str) -> None:
        self.primary.configure(state=tk.DISABLED if busy else tk.NORMAL)
        self.progress.configure(text=message, fg=WARNING)

    def _drain_queue(self) -> None:
        try:
            while True:
                kind, payload = self._queue.get_nowait()
                if kind == "status":
                    self._display_status(payload)  # type: ignore[arg-type]
                elif kind == "voice-status":
                    self._display_voice_status(payload)  # type: ignore[arg-type]
                elif kind == "voice-error":
                    self.voice_detail.configure(text=str(payload), fg=ERROR)
                    self.voice_button.configure(
                        state=tk.NORMAL,
                        text="Tentar baixar novamente",
                        command=self._download_voice_model,
                    )
                elif kind == "natural-voice-status":
                    self._display_natural_voice_status()
                elif kind == "natural-voice-error":
                    self.natural_voice_detail.configure(text=str(payload), fg=ERROR)
                    self.natural_voice_button.configure(
                        state=tk.NORMAL,
                        text="Tentar baixar novamente",
                        command=self._download_natural_voice,
                    )
                else:
                    self._set_busy(False, str(payload))
                    self.progress.configure(fg=ERROR)
        except Empty:
            pass
        finally:
            try:
                self.root.after(50, self._drain_queue)
            except tk.TclError:
                pass

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    SetupApp().run()


if __name__ == "__main__":
    main()
