from __future__ import annotations

from collections.abc import Iterable

from ubuntu_ai.tools.capability import ToolCapability


class CapabilityRegistry:
    """Catálogo central das capacidades conhecidas pelo agente."""

    def __init__(self, capabilities: Iterable[ToolCapability] = ()) -> None:
        self._capabilities: dict[str, ToolCapability] = {}
        for capability in capabilities:
            self.register(capability)

    def register(
        self,
        capability: ToolCapability,
        *,
        replace: bool = False,
    ) -> None:
        key = capability.name.strip().lower()
        if key in self._capabilities and not replace:
            raise ValueError(f"Capacidade já registrada: {capability.name}")
        self._capabilities[key] = capability

    def get(self, name: str) -> ToolCapability:
        key = name.strip().lower()
        try:
            return self._capabilities[key]
        except KeyError as exc:
            raise KeyError(f"Capacidade não encontrada: {name}") from exc

    def all(self) -> tuple[ToolCapability, ...]:
        return tuple(sorted(self._capabilities.values(), key=lambda item: item.name))

    def for_executable(self, executable: str) -> tuple[ToolCapability, ...]:
        return tuple(
            capability
            for capability in self.all()
            if capability.supports_executable(executable)
        )
