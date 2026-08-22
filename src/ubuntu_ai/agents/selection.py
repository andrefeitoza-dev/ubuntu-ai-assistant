from __future__ import annotations

import unicodedata
from dataclasses import dataclass

from ubuntu_ai.agents.coordinator import AgentCoordinator
from ubuntu_ai.agents.models import AgentKind
from ubuntu_ai.agents.orchestration import (
    MultiAgentOrchestrator,
    OrchestrationGoal,
    OrchestrationTask,
)
from ubuntu_ai.agents.registry import AgentRegistry
from ubuntu_ai.agents.specialists import (
    AgentEnvironment,
    NetworkAgent,
    ServicesAgent,
    SpecialistAction,
    SpecialistPayload,
    StorageAgent,
    SystemAgent,
)


@dataclass(frozen=True, slots=True)
class SpecialistSelection:
    specialists: tuple[AgentKind, ...]
    reason: str


class SpecialistSelector:
    """Seleciona somente especialistas sustentados pela solicitação explícita."""

    _ORDER = (
        AgentKind.SYSTEM,
        AgentKind.NETWORK,
        AgentKind.STORAGE,
        AgentKind.SERVICES,
    )
    _KEYWORDS = {
        AgentKind.SYSTEM: frozenset(
            {"sistema", "computador", "cpu", "memoria", "kernel", "processos", "uptime"}
        ),
        AgentKind.NETWORK: frozenset(
            {"rede", "internet", "ip", "dns", "gateway", "rota", "conectividade"}
        ),
        AgentKind.STORAGE: frozenset(
            {"disco", "discos", "armazenamento", "particao", "particoes", "espaco"}
        ),
        AgentKind.SERVICES: frozenset(
            {"servico", "servicos", "systemd", "systemctl", "daemon", "falha"}
        ),
    }
    _ALL_MARKERS = (
        "diagnostico completo",
        "diagnosticar tudo",
        "verificacao completa",
        "saude do computador",
    )

    def select(self, request: str) -> SpecialistSelection:
        normalized = _normalize(request)
        if not normalized:
            raise ValueError("A solicitação de orquestração não pode estar vazia.")

        if any(marker in normalized for marker in self._ALL_MARKERS):
            return SpecialistSelection(
                specialists=self._ORDER,
                reason="Diagnóstico completo solicitado explicitamente.",
            )

        words = set(normalized.split())
        selected = tuple(kind for kind in self._ORDER if words & self._KEYWORDS[kind])
        if not selected:
            raise ValueError("Nenhum especialista corresponde explicitamente à solicitação.")
        return SpecialistSelection(
            specialists=selected,
            reason="Especialistas selecionados pelos domínios citados na solicitação.",
        )


class OrchestrationPlanner:
    """Converte uma solicitação em objetivo multiagente somente leitura."""

    _ACTIONS = {
        AgentKind.SYSTEM: SpecialistAction(("uptime",)),
        AgentKind.NETWORK: SpecialistAction(("ip", "route")),
        AgentKind.STORAGE: SpecialistAction(("df", "-h")),
        AgentKind.SERVICES: SpecialistAction(("systemctl", "--failed", "--no-legend", "--plain")),
    }

    def __init__(self, selector: SpecialistSelector | None = None) -> None:
        self._selector = selector or SpecialistSelector()

    def plan(
        self,
        request: str,
        *,
        goal_id: str,
        environment: AgentEnvironment = AgentEnvironment.LOCAL,
        target: str | None = None,
    ) -> OrchestrationGoal:
        selection = self._selector.select(request)
        if environment is AgentEnvironment.REMOTE and not target:
            raise ValueError("A orquestração remota exige destino explícito.")

        selected_target = target or "local"
        context = {
            "environment": environment.value,
            "target": selected_target,
            "selection_reason": selection.reason,
        }
        tasks = tuple(
            OrchestrationTask(
                task_id=f"{index:02d}-{kind.value}",
                specialist=kind,
                payload=SpecialistPayload(
                    request=request,
                    actions=(self._ACTIONS[kind],),
                    environment=environment,
                    target=target,
                ),
                context_keys=frozenset({"environment", "target"}),
            )
            for index, kind in enumerate(selection.specialists, start=1)
        )
        return OrchestrationGoal(
            goal_id=goal_id,
            description=request,
            tasks=tasks,
            context=context,
        )


def build_specialist_orchestrator() -> MultiAgentOrchestrator:
    """Compõe somente os quatro especialistas operacionais permitidos."""

    registry = AgentRegistry()
    registry.register(SystemAgent())
    registry.register(NetworkAgent())
    registry.register(StorageAgent())
    registry.register(ServicesAgent())
    return MultiAgentOrchestrator(AgentCoordinator(registry))


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip().lower())
    return " ".join(
        "".join(character for character in normalized if not unicodedata.combining(character))
        .replace("?", " ")
        .replace(",", " ")
        .replace(".", " ")
        .split()
    )
