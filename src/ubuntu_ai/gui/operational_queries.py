from __future__ import annotations

import subprocess
import unicodedata
from collections.abc import Iterable
from typing import Any

import psutil


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
    _AUDIT = {
        "mostre o historico de acoes",
        "liste as acoes recentes",
        "mostre a auditoria local",
    }
    _LEARNING = {
        "o assistente aprende com o uso",
        "mostre o aprendizado do assistente",
        "mostre o status do aprendizado",
    }
    _RESOURCE_USAGE = {
        "quanto de memoria o assistente usa",
        "mostre o consumo de memoria do assistente",
        "quanta ram o ubuntu ai usa",
    }

    @classmethod
    def matches(cls, phrase: str) -> bool:
        return cls._topic_for(phrase) is not None

    def respond(
        self,
        phrase: str,
        *,
        tasks: Iterable[Any] = (),
        schedules: Iterable[Any] = (),
        profiles: Iterable[Any] = (),
        plugins: Iterable[Any] = (),
        audit_records: Iterable[Any] = (),
        learning_stats: Any | None = None,
    ) -> str | None:
        topic = self._topic_for(phrase)

        if topic == "updates":
            return self._updates()
        if topic == "automations":
            return self._tasks(tasks)
        if topic == "schedules":
            return self._schedules(schedules)
        if topic == "profiles":
            return self._profiles(profiles)
        if topic == "plugins":
            return self._plugins(plugins)
        if topic == "audit":
            return self._audit(audit_records)
        if topic == "learning":
            return self._learning(learning_stats)
        if topic == "resource_usage":
            return self._resource_usage()
        return None

    @classmethod
    def _topic_for(cls, phrase: str) -> str | None:
        normalized = cls._normalize(phrase)
        if normalized in cls._UPDATES:
            return "updates"
        if normalized in cls._AUTOMATIONS:
            return "automations"
        if normalized in cls._SCHEDULES:
            return "schedules"
        if normalized in cls._PROFILES:
            return "profiles"
        if normalized in cls._PLUGINS:
            return "plugins"
        if normalized in cls._AUDIT:
            return "audit"
        if normalized in cls._LEARNING:
            return "learning"
        if normalized in cls._RESOURCE_USAGE:
            return "resource_usage"

        words = set(normalized.split())
        query = bool(words & {"exiba", "ha", "liste", "mostre", "quais"})
        if (
            query
            and words & {"atualizacao", "atualizacoes", "pacotes"}
            and words
            & {
                "atualizar",
                "disponiveis",
            }
        ):
            return "updates"
        if query and words & {"automacao", "automacoes"}:
            return "automations"
        if (
            query
            and words & {"tarefa", "tarefas"}
            and words
            & {
                "ativas",
                "execucao",
                "registradas",
            }
        ):
            return "automations"
        if query and words & {"agendamento", "agendamentos"}:
            return "schedules"
        if (
            query
            and words & {"agente", "agentes"}
            and words
            & {
                "disponiveis",
                "perfil",
                "perfis",
            }
        ):
            return "profiles"
        if (
            query
            and words & {"plugin", "plugins"}
            and words
            & {
                "carregados",
                "catalogo",
                "disponiveis",
            }
        ):
            return "plugins"
        if (
            query
            and words & {"acao", "acoes", "auditoria", "historico"}
            and words
            & {
                "auditoria",
                "historico",
                "recentes",
            }
        ):
            return "audit"
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
    def _audit(records: Iterable[Any]) -> str:
        items = tuple(records)
        if not items:
            return "Nenhuma ação local foi registrada na auditoria."
        lines = [f"Ações locais auditadas: {len(items)} evento(s) recente(s)."]
        for record in items:
            target = getattr(record, "target", None) or "sem alvo"
            lines.append(f"• {record.timestamp} · {record.status} · {record.intent} · {target}")
        lines.append("Comandos sensíveis e saídas não são exibidos nesta consulta.")
        return "\n".join(lines)

    @staticmethod
    def _learning(stats: Any | None) -> str:
        if stats is None:
            return "O mecanismo de aprendizado não está disponível nesta sessão."
        return (
            "Aprendizado persistente do assistente:\n"
            f"• padrões registrados: {stats.patterns}\n"
            f"• tentativas observadas: {stats.attempts}\n"
            f"• sucessos: {stats.successes}\n"
            f"• falhas: {stats.failures}\n"
            f"• bloqueios de segurança: {stats.blocked}\n"
            f"• padrões aprovados explicitamente para reutilização: "
            f"{stats.approved_for_reuse}\n"
            "A execução aprendida continua subordinada à política de segurança."
        )

    @staticmethod
    def _resource_usage() -> str:
        process = psutil.Process()
        processes = (process, *process.children(recursive=True))
        rss = sum(item.memory_info().rss for item in processes)
        threads = sum(item.num_threads() for item in processes)
        return (
            "Uso atual do Ubuntu AI Assistant:\n"
            f"• memória residente: {rss / (1024 * 1024):.1f} MiB\n"
            f"• processos considerados: {len(processes)}\n"
            f"• threads: {threads}\n"
            "A medição inclui processos filhos ativos neste instante."
        )

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.strip().lower())
        ascii_text = "".join(
            character for character in normalized if not unicodedata.combining(character)
        )
        return " ".join(ascii_text.rstrip("?.!").split())
