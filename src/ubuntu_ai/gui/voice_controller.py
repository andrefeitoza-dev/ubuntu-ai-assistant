from __future__ import annotations

import threading
import tkinter as tk

from ubuntu_ai.gui.theme import ERROR, SUCCESS, TEXT_MUTED, WARNING
from ubuntu_ai.voice import VoiceInputService, VoiceOutputService


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
        self.voice_button.configure(state=tk.NORMAL, text=">> voice input")
        self.status_label.configure(text="●  Voz reconhecida", fg=SUCCESS)
        self.submit(
            request_override=text,
            display_request="Solicitação recebida por voz.",
        )

    def _deliver_voice_error(self, message: str) -> None:
        self.voice_button.configure(state=tk.NORMAL, text=">> voice input")
        self.status_label.configure(text="●  Voz não reconhecida", fg=ERROR)
        self._add_system_message(message, color=ERROR)
        self.request_entry.focus_set()

    def _toggle_speech_output(self) -> None:
        service = getattr(self, "_voice_output", None) or VoiceOutputService()
        self._voice_output = service
        if not service.available:
            self._add_system_message(
                "A voz de saída não está disponível. Instale o speech-dispatcher do Ubuntu.",
                color=WARNING,
            )
            return
        self._speech_enabled = not getattr(self, "_speech_enabled", False)
        tone = SUCCESS if self._speech_enabled else TEXT_MUTED
        self.speech_button.configure(text="voice output", fg=tone)
        if self._speech_enabled:
            service.speak_async("Voz do assistente ativada.")

    def _speak_response(self, message: str) -> None:
        if not getattr(self, "_speech_enabled", False):
            return
        service = getattr(self, "_voice_output", None)
        if service is not None:
            service.speak_async(message)
