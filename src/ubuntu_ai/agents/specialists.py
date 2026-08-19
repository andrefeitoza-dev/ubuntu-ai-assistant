from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ubuntu_ai.agents.base import BaseAgent
from ubuntu_ai.agents.models import AgentKind, AgentResult, AgentTask
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.reflection.failure import FailureKind


class AgentEnvironment(StrEnum):
    LOCAL = "local"
    REMOTE = "remote"


@dataclass(frozen=True, slots=True)
class SpecialistAction:
    argv: tuple[str, ...]
    risk: RiskLevel = RiskLevel.LOW

    def __post_init__(self) -> None:
        if not self.argv or any(not value.strip() for value in self.argv):
            raise ValueError("A ação especializada exige argumentos válidos.")


@dataclass(frozen=True, slots=True)
class SpecialistPayload:
    request: str
    actions: tuple[SpecialistAction, ...]
    environment: AgentEnvironment = AgentEnvironment.LOCAL
    target: str | None = None
    attempt: int = 1
    elapsed_seconds: float = 0.0
    confirmed: bool = False


@dataclass(frozen=True, slots=True)
class SpecialistPlan:
    specialist: AgentKind
    environment: AgentEnvironment
    target: str
    actions: tuple[SpecialistAction, ...]


@dataclass(frozen=True, slots=True)
class SpecialistLimits:
    executables: frozenset[str]
    max_actions: int = 5
    max_attempts: int = 3
    max_duration: float = 300.0


class SpecialistAgent(BaseAgent):
    """Valida planos de uma especialidade sem executar ou elevar privilégios."""

    kind: AgentKind
    limits: SpecialistLimits

    def handle(self, task: AgentTask) -> AgentResult:
        payload = task.payload
        if not isinstance(payload, SpecialistPayload):
            raise TypeError("Payload inválido para agente especializado.")
        self._validate(payload)
        return AgentResult(
            kind=self.kind,
            output=SpecialistPlan(
                specialist=self.kind,
                environment=payload.environment,
                target=payload.target or "local",
                actions=payload.actions,
            ),
        )

    def replan_guidance(self, failure: FailureKind) -> str:
        guidance = {
            FailureKind.PERMISSION: (
                "Solicite autorização; não tente sudo ou elevação automática."
            ),
            FailureKind.NOT_FOUND: "Verifique a existência do recurso antes de repetir.",
            FailureKind.NETWORK: "Valide conectividade e destino antes de nova tentativa.",
            FailureKind.TIMEOUT: "Reduza o escopo e respeite o limite de duração.",
        }
        return guidance.get(
            failure,
            "Reavalie as evidências e não repita a mesma ação sem corrigir a causa.",
        )

    def _validate(self, payload: SpecialistPayload) -> None:
        if not payload.request.strip():
            raise ValueError("A solicitação especializada não pode estar vazia.")
        if payload.environment is AgentEnvironment.REMOTE and not payload.target:
            raise PermissionError("Operações remotas exigem destino explícito.")
        if payload.attempt < 1 or payload.attempt > self.limits.max_attempts:
            raise PermissionError("Limite de tentativas do agente atingido.")
        if not 0 <= payload.elapsed_seconds <= self.limits.max_duration:
            raise PermissionError("Limite de duração do agente atingido.")
        if not payload.actions or len(payload.actions) > self.limits.max_actions:
            raise PermissionError("Quantidade de ações fora do limite do agente.")

        for action in payload.actions:
            executable = action.argv[0]
            if executable not in self.limits.executables:
                raise PermissionError(f"O agente {self.kind.value} não permite '{executable}'.")
            if executable in {"sudo", "su", "doas", "pkexec"}:
                raise PermissionError("Elevação automática não é permitida.")
            if action.risk is RiskLevel.CRITICAL:
                raise PermissionError("Ações CRITICAL não são delegadas a agentes.")
            if action.risk is not RiskLevel.LOW and not payload.confirmed:
                raise PermissionError("A ação sensível exige confirmação explícita.")


class SystemAgent(SpecialistAgent):
    kind = AgentKind.SYSTEM
    limits = SpecialistLimits(frozenset({"hostnamectl", "uname", "uptime", "ps", "free"}))


class NetworkAgent(SpecialistAgent):
    kind = AgentKind.NETWORK
    limits = SpecialistLimits(frozenset({"ip", "ss", "ping", "resolvectl"}))


class StorageAgent(SpecialistAgent):
    kind = AgentKind.STORAGE
    limits = SpecialistLimits(frozenset({"lsblk", "df", "du", "find"}))


class ServicesAgent(SpecialistAgent):
    kind = AgentKind.SERVICES
    limits = SpecialistLimits(frozenset({"systemctl", "journalctl"}))
