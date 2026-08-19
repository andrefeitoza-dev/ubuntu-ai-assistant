from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from ubuntu_ai.agents.models import AgentKind

_PROFILE_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
_ELEVATION = frozenset({"sudo", "su", "doas", "pkexec"})
_SPECIALIST_LIMITS: dict[AgentKind, tuple[frozenset[str], int, int, float]] = {
    AgentKind.SYSTEM: (frozenset({"hostnamectl", "uname", "uptime", "ps", "free"}), 5, 3, 300.0),
    AgentKind.NETWORK: (frozenset({"ip", "ss", "ping", "resolvectl"}), 5, 3, 300.0),
    AgentKind.STORAGE: (frozenset({"lsblk", "df", "du", "find"}), 5, 3, 300.0),
    AgentKind.SERVICES: (frozenset({"systemctl", "journalctl"}), 5, 3, 300.0),
}


@dataclass(frozen=True, slots=True)
class AgentProfile:
    name: str
    kind: AgentKind
    executables: frozenset[str]
    environments: frozenset[str] = frozenset({"local"})
    max_actions: int = 3
    max_attempts: int = 2
    max_duration: float = 120.0
    allow_sensitive: bool = False

    def __post_init__(self) -> None:
        if not _PROFILE_NAME.fullmatch(self.name):
            raise ValueError("Nome de perfil inválido.")
        if self.kind not in _SPECIALIST_LIMITS:
            raise ValueError("Perfis são aceitos apenas para agentes especializados.")
        if not self.executables or self.executables & _ELEVATION:
            raise ValueError("Executáveis vazios ou de elevação não são permitidos.")
        if not self.environments or not self.environments <= {"local", "remote"}:
            raise ValueError("Ambiente de perfil inválido.")
        if self.max_actions < 1 or self.max_attempts < 1 or self.max_duration <= 0:
            raise ValueError("Os limites do perfil devem ser positivos.")


class AgentProfilePolicy:
    """Garante que perfis somente reduzam os limites internos."""

    @staticmethod
    def validate(profile: AgentProfile) -> None:
        executables, actions, attempts, duration = _SPECIALIST_LIMITS[profile.kind]
        if not profile.executables <= executables:
            raise PermissionError("O perfil tenta ampliar executáveis do agente.")
        if profile.max_actions > actions:
            raise PermissionError("O perfil tenta ampliar a quantidade de ações.")
        if profile.max_attempts > attempts:
            raise PermissionError("O perfil tenta ampliar o limite de tentativas.")
        if profile.max_duration > duration:
            raise PermissionError("O perfil tenta ampliar o limite de duração.")


class AgentProfileRepository:
    """Persiste perfis não secretos em JSON com permissão 0600."""

    def __init__(self, path: Path) -> None:
        self._path = path.expanduser()
        self._policy = AgentProfilePolicy()

    def save(self, profiles: tuple[AgentProfile, ...]) -> None:
        names: set[str] = set()
        for profile in profiles:
            self._policy.validate(profile)
            if profile.name in names:
                raise ValueError(f"Perfil duplicado: {profile.name}")
            names.add(profile.name)
        payload = [
            {
                "name": item.name,
                "kind": item.kind.value,
                "executables": sorted(item.executables),
                "environments": sorted(item.environments),
                "max_actions": item.max_actions,
                "max_attempts": item.max_attempts,
                "max_duration": item.max_duration,
                "allow_sensitive": item.allow_sensitive,
            }
            for item in sorted(profiles, key=lambda value: value.name)
        ]
        self._path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        temporary = self._path.with_suffix(f"{self._path.suffix}.tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        temporary.replace(self._path)
        self._path.chmod(0o600)

    def load(self) -> tuple[AgentProfile, ...]:
        if not self._path.is_file():
            return ()
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            raise ValueError("O catálogo de perfis deve conter uma lista.")
        profiles = tuple(
            AgentProfile(
                name=str(item["name"]),
                kind=AgentKind(item["kind"]),
                executables=frozenset(item["executables"]),
                environments=frozenset(item.get("environments", ["local"])),
                max_actions=int(item.get("max_actions", 3)),
                max_attempts=int(item.get("max_attempts", 2)),
                max_duration=float(item.get("max_duration", 120.0)),
                allow_sensitive=bool(item.get("allow_sensitive", False)),
            )
            for item in raw
        )
        for profile in profiles:
            self._policy.validate(profile)
        return profiles


def default_agent_profiles() -> tuple[AgentProfile, ...]:
    profiles = (
        AgentProfile(
            name=f"{kind.value}-readonly",
            kind=kind,
            executables=executables,
        )
        for kind, (executables, _actions, _attempts, _duration) in _SPECIALIST_LIMITS.items()
    )
    return tuple(sorted(profiles, key=lambda profile: profile.name))
