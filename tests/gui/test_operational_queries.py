from __future__ import annotations

from datetime import UTC, datetime
from types import SimpleNamespace

from ubuntu_ai.agents import default_agent_profiles
from ubuntu_ai.audit import LocalActionAuditRecord
from ubuntu_ai.autonomy.scheduler import AutomationRisk, ScheduledAutomation
from ubuntu_ai.gui.operational_queries import OperationalQueryResponder
from ubuntu_ai.learning import LearningStats


def responder() -> OperationalQueryResponder:
    return OperationalQueryResponder()


def test_lists_real_automation_tasks() -> None:
    task = SimpleNamespace(
        task_id="task-1",
        status=SimpleNamespace(value="running"),
        completed_steps=2,
        total_steps=4,
        description="Diagnóstico de rede",
    )

    response = responder().respond("Mostre minhas automações.", tasks=(task,))

    assert "task-1" in response
    assert "running" in response
    assert "2/4" in response


def test_distinguishes_assistant_tasks_from_system_processes() -> None:
    response = responder().respond("Quais tarefas estão em execução?")

    assert response == "Não existem tarefas do assistente registradas."


def test_lists_registered_schedules() -> None:
    item = ScheduledAutomation(
        schedule_id="schedule-1",
        task_id="task-1",
        run_at=datetime(2026, 8, 28, 12, 0, tzinfo=UTC),
        risk=AutomationRisk.LOW,
    )

    response = responder().respond("Mostre meus agendamentos.", schedules=(item,))

    assert "schedule-1" in response
    assert "task-1" in response
    assert "low" in response


def test_lists_restrictive_agent_profiles() -> None:
    response = responder().respond(
        "Mostre os perfis de agentes.",
        profiles=default_agent_profiles(),
    )

    assert "Perfis de agentes disponíveis: 4." in response
    assert "não permite ações sensíveis" in response


def test_reports_empty_plugin_registry_honestly() -> None:
    response = responder().respond("Mostre o catálogo de plugins.")

    assert "Nenhum plugin está carregado" in response
    assert "validação e admissão" in response


def test_unknown_request_is_not_claimed() -> None:
    assert responder().respond("Conte uma história.") is None


def test_lists_redacted_local_action_audit() -> None:
    record = LocalActionAuditRecord(
        timestamp="2026-08-30T18:00:00+00:00",
        session_id="session-1",
        request="Abra o Firefox",
        intent="Abrir aplicativo",
        target="firefox",
        command=("gtk-launch", "firefox"),
        policy_reason="Comando autorizado.",
        status="executed",
        message="Solicitação enviada.",
        return_code=0,
        duration=0.1,
    )

    response = responder().respond("Mostre o histórico de ações.", audit_records=(record,))

    assert "Abrir aplicativo" in response
    assert "firefox" in response
    assert "gtk-launch" not in response
    assert "Comandos sensíveis" in response


def test_reports_learning_without_exposing_patterns() -> None:
    stats = LearningStats(3, 7, 5, 1, 1, 2)

    response = responder().respond("O assistente aprende com o uso?", learning_stats=stats)

    assert "padrões registrados: 3" in response
    assert "sucessos: 5" in response
    assert "aprovados explicitamente" in response


def test_reports_current_assistant_memory_usage() -> None:
    response = responder().respond("Quanto de memória o assistente usa?")

    assert "memória residente" in response
    assert "MiB" in response
    assert "processos considerados" in response
