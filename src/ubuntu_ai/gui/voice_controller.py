from __future__ import annotations

import threading
import tkinter as tk

from ubuntu_ai.gui.theme import ERROR, SUCCESS, WARNING
from ubuntu_ai.voice import VoiceInputService


class VoiceControllerMixin:
    """Coordena voz local sem expor a transcrição na interface."""

    def _start_voice_input(self) -> None:
        if self._busy:
            return
        service = VoiceInputService()
        availability = service.availability()
        if not availability.available:
            self._add_system_message(
                availability.message
                + " A voz é opcional e o assistente continua funcionando por texto.",
                color=WARNING,
            )
            return
        self.voice_button.configure(state=tk.DISABLED, text="Ouvindo…")
        self.status_label.configure(text="●  Ouvindo por até 7 segundos…", fg=WARNING)
        threading.Thread(target=self._voice_worker, args=(service,), daemon=True).start()

    def _voice_worker(self, service: VoiceInputService) -> None:
        try:
            text = service.listen()
        except Exception as exc:
            self._post_to_ui(self._deliver_voice_error, str(exc))
            return
        self._post_to_ui(self._deliver_voice_text, text)

    def _deliver_voice_text(self, text: str) -> None:
        self.voice_button.configure(state=tk.NORMAL, text="Falar")
        self.status_label.configure(text="●  Voz reconhecida", fg=SUCCESS)
        self.submit(
            request_override=text,
            display_request="Solicitação recebida por voz.",
        )

    def _deliver_voice_error(self, message: str) -> None:
        self.voice_button.configure(state=tk.NORMAL, text="Falar")
        self.status_label.configure(text="●  Voz não reconhecida", fg=ERROR)
        self._add_system_message(message, color=ERROR)
        self.request_entry.focus_set()
