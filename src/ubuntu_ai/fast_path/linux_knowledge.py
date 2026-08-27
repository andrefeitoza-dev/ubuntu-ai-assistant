from __future__ import annotations

import re
import unicodedata


class LinuxKnowledgeResponder:
    """Explicações fundamentais, estáveis e independentes do Ollama."""

    _RESPONSES = {
        "explique como funciona o systemd": (
            "O systemd é o gerenciador de inicialização e serviços usado pelo "
            "Ubuntu. Ele é iniciado como processo PID 1, organiza recursos em "
            "unidades, resolve dependências e pode iniciar serviços em paralelo. "
            "O comando systemctl consulta e controla as unidades; o journalctl "
            "consulta os registros mantidos pelo systemd-journald."
        ),
        "o que e um servico": (
            "Um serviço é um processo ou conjunto de processos que fornece uma "
            "função do sistema em segundo plano, como rede, SSH ou impressão. "
            "No Ubuntu, serviços normalmente são representados por unidades "
            ".service do systemd e podem ser consultados, iniciados, parados ou "
            "configurados para iniciar durante o boot."
        ),
    }

    def respond(self, request: str) -> str | None:
        return self._RESPONSES.get(self._normalize(request))

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.encode("ascii", "ignore").decode().lower()
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        return " ".join(normalized.split())
