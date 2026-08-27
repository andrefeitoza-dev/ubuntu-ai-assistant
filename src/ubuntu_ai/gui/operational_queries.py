from __future__ import annotations

import subprocess
import unicodedata
from collections.abc import Iterable
from typing import Any


class OperationalQueryResponder:
    """Consulta estado operacional sem executar alterações."""

    _UPDATES = {
        "quais atualizacoes estao disponiveis",
        "mostre as atualizacoes disponiveis",
    }
    _AUTOMATIONS = {
        "mostre minhas automacoes",
        "quais tarefas estao em execucao",
        "mostre minhas tarefas",
    }
    _SCHEDULES = {
        "mostre meus agendamentos",
        "quais agendamentos estao registrados",
    }
    _PROFILES = {
        "mostre os perfis de agentes",
        "quais sao os perfis de agentes",
    }
    _PLUGINS = {
        "mostre o catalogo de plugins",
        "quais plugins estao carregados",
    }

    @classmethod
    def matches(cls, phrase: str) -> bool:
        normalized = cls._normalize(phrase)
        return normalized in (
            cls._UPDATES | cls._AUTOMATIONS | cls._SCHEDULES | cls._PROFILES | cls._PLUGINS
        )

    def respond(
        self,
        phrase: str,
        *,
        tasks: Iterable[Any] = (),
        schedules: Iterable[Any] = (),
        profiles: Iterable[Any] = (),
        plugins: Iterable[Any] = (),
    ) -> str | None:
        normalized = self._normalize(phrase)

        if normalized in self._UPDATES:
            return self._updates()
        if normalized in self._AUTOMATIONS:
            return self._tasks(tasks)
        if normalized in self._SCHEDULES:
            return self._schedules(schedules)
        if normalized in self._PROFILES:
            return self._profiles(profiles)
        if normalized in self._PLUGINS:
            return self._plugins(plugins)
        return None

    @staticmethod
    def _updates() -> str:
        try:
            result = subprocess.run(
                ("apt", "list", "--upgradable"),
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
                shell=False,
            )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return "Não foi possível consultar o cache local do APT."

        if result.returncode != 0:
            return "O cache local do APT não pôde ser consultado."

        packages = tuple(
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip() and not line.startswith("Listing")
        )
        if not packages:
            return "O cache local do APT não indica atualizações disponíveis."

        preview = packages[:20]
        lines = [f"Atualizações disponíveis no cache local do APT: {len(packages)}."]
        lines.extend(f"• {package}" for package in preview)
        if len(packages) > len(preview):
            lines.append(f"• … e mais {len(packages) - len(preview)} pacote(s).")
        lines.append("Nenhuma atualização foi baixada ou instalada.")
        return "\n".join(lines)

    @staticmethod
    def _tasks(tasks: Iterable[Any]) -> str:
        items = tuple(tasks)
        if not items:
            return "Não existem tarefas do assistente registradas."

        lines = [f"Tarefas do assistente: {len(items)}."]
        for task in items:
            status = getattr(getattr(task, "status", ""), "value", "")
            completed = getattr(task, "completed_steps", 0)
            total = getattr(task, "total_steps", 0)
            description = getattr(task, "description", "")
            lines.append(
                f"• {task.task_id} · {status or 'desconhecido'} · "
                f"{completed}/{total} · {description}"
            )
        return "\n".join(lines)

    @staticmethod
    def _schedules(schedules: Iterable[Any]) -> str:
        items = tuple(schedules)
        if not items:
            return "Não existem agendamentos locais registrados."

        lines = [f"Agendamentos locais: {len(items)}."]
        for item in items:
            risk = getattr(getattr(item, "risk", ""), "value", "")
            lines.append(
                f"• {item.schedule_id} · tarefa {item.task_id} · "
                f"{item.run_at.isoformat()} · risco {risk or 'desconhecido'}"
            )
        return "\n".join(lines)

    @staticmethod
    def _profiles(profiles: Iterable[Any]) -> str:
        items = tuple(profiles)
        lines = [f"Perfis de agentes disponíveis: {len(items)}."]
        for profile in items:
            kind = getattr(getattr(profile, "kind", ""), "value", "")
            environments = ", ".join(sorted(profile.environments))
            sensitivity = (
                "permite ações sensíveis"
                if profile.allow_sensitive
                else "não permite ações sensíveis"
            )
            lines.append(f"• {profile.name} · {kind} · {environments} · {sensitivity}")
        return "\n".join(lines)

    @staticmethod
    def _plugins(plugins: Iterable[Any]) -> str:
        items = tuple(plugins)
        if not items:
            return (
                "Nenhum plugin está carregado. Plugins somente aparecem após "
                "validação e admissão pela política do assistente."
            )

        lines = [f"Plugins carregados: {len(items)}."]
        for loaded in items:
            manifest = loaded.manifest
            version = getattr(manifest, "version", "versão não informada")
            lines.append(f"• {manifest.name} · {version}")
        return "\n".join(lines)

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.strip().lower())
        ascii_text = "".join(
            character for character in normalized if not unicodedata.combining(character)
        )
        return " ".join(ascii_text.rstrip("?.!").split())
