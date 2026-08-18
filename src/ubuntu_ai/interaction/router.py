from __future__ import annotations

import re
import shlex
import unicodedata
from dataclasses import dataclass
from enum import StrEnum

from ubuntu_ai.fast_path import LocalResponder
from ubuntu_ai.planner.builtin import BuiltinPlanner


class InteractionRoute(StrEnum):
    LOCAL = "local"
    ACTION = "action"
    CHAT = "chat"


@dataclass(frozen=True, slots=True)
class InteractionDecision:
    route: InteractionRoute
    response: str | None = None


class InteractionRouter:
    """Separa conversa, respostas locais e ações auditáveis do sistema."""

    _INFORMATION_PREFIXES = (
        "como ",
        "o que e",
        "o que sao",
        "quem e",
        "explique",
        "como funciona",
        "como usar",
        "como faco",
        "como fazer",
        "por que",
        "qual a diferenca",
        "qual e a diferenca",
        "me fale sobre",
        "fale sobre",
        "defina",
        "mostre como",
    )
    _ACTION_VERBS = {
        "apague",
        "atualize",
        "cancele",
        "configure",
        "conserte",
        "copie",
        "crie",
        "desinstale",
        "diagnostique",
        "execute",
        "finalize",
        "habilite",
        "inicie",
        "instale",
        "liste",
        "mate",
        "mostre",
        "mova",
        "pare",
        "reinicie",
        "remova",
        "renomeie",
        "verifique",
    }
    _SYSTEM_TERMS = {
        "apt",
        "arquivo",
        "arquivos",
        "armazenamento",
        "branch",
        "cpu",
        "diretorio",
        "disco",
        "docker",
        "git",
        "gpu",
        "hostname",
        "ip",
        "kernel",
        "memoria",
        "nginx",
        "pacote",
        "pasta",
        "pastas",
        "processador",
        "processo",
        "processos",
        "ram",
        "rede",
        "repositorio",
        "servico",
        "servicos",
        "sistema",
        "swap",
        "systemd",
        "usuario",
        "wifi",
    }
    _SHELL_COMMANDS = {
        "cat",
        "df",
        "docker",
        "free",
        "git",
        "hostname",
        "ip",
        "ls",
        "lscpu",
        "mkdir",
        "ps",
        "pwd",
        "systemctl",
        "uname",
        "uptime",
        "whoami",
    }

    def __init__(
        self,
        local_responder: LocalResponder | None = None,
        builtin_planner: BuiltinPlanner | None = None,
    ) -> None:
        self._local_responder = local_responder or LocalResponder()
        self._builtin_planner = builtin_planner or BuiltinPlanner()

    def route(self, request: str) -> InteractionDecision:
        normalized = self._normalize(request)
        if not normalized:
            raise ValueError("Digite uma solicitação.")

        local = self._local_responder.respond(request)
        if local is not None:
            return InteractionDecision(InteractionRoute.LOCAL, local.text)

        if normalized.startswith(self._INFORMATION_PREFIXES):
            return InteractionDecision(InteractionRoute.CHAT)

        if self._builtin_planner.try_create_plan(request) is not None:
            return InteractionDecision(InteractionRoute.ACTION)

        words = set(normalized.split())
        if self._looks_like_shell_command(normalized):
            return InteractionDecision(InteractionRoute.ACTION)

        if words & self._ACTION_VERBS and words & self._SYSTEM_TERMS:
            return InteractionDecision(InteractionRoute.ACTION)

        return InteractionDecision(InteractionRoute.CHAT)

    @classmethod
    def _looks_like_shell_command(cls, request: str) -> bool:
        try:
            parts = shlex.split(request)
        except ValueError:
            return False
        if not parts:
            return False
        executable = parts[1] if parts[0] == "sudo" and len(parts) > 1 else parts[0]
        return executable in cls._SHELL_COMMANDS or executable == "apt"

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value)
        normalized = normalized.encode("ascii", "ignore").decode().lower()
        normalized = re.sub(r"[^a-z0-9_./\s-]", " ", normalized)
        return " ".join(normalized.split())
