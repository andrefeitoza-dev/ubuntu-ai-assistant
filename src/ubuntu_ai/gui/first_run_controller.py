from __future__ import annotations

import subprocess
import sys
import threading

from ubuntu_ai.distribution.first_run import FirstRunSetup, FirstRunStatus
from ubuntu_ai.gui.conversation_view import add_setup_prompt


class FirstRunControllerMixin:
    """Detecta a IA local e oferece configuração sem bloquear o Tkinter."""

    def _check_ai_setup(self) -> None:
        threading.Thread(target=self._check_ai_setup_worker, daemon=True).start()

    def _check_ai_setup_worker(self) -> None:
        try:
            status = FirstRunSetup().status()
        except Exception:
            return
        self._post_to_ui(self._deliver_ai_setup_status, status)

    def _deliver_ai_setup_status(self, status: FirstRunStatus) -> None:
        if status.ready or not self.welcome.winfo_exists():
            return
        self._setup_prompt = add_setup_prompt(
            self.welcome,
            ollama_available=status.ollama_available,
            model=status.model,
            on_configure=self._open_ai_setup,
        )

    @staticmethod
    def _open_ai_setup() -> None:
        subprocess.Popen(
            (sys.executable, "-m", "ubuntu_ai.gui.setup"),
            close_fds=True,
            shell=False,
            start_new_session=True,
        )
