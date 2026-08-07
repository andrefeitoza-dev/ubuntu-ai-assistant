from __future__ import annotations

from collections.abc import Callable

from ubuntu_ai.hardening.models import (
    ComponentHealth,
    HealthReport,
    HealthStatus,
)

HealthProbe = Callable[[], bool]


class ApplicationHealthService:
    """Agrega probes leves sem executar ações destrutivas."""

    def __init__(self) -> None:
        self._probes: dict[str, HealthProbe] = {}

    def register(
        self,
        name: str,
        probe: HealthProbe,
        *,
        replace: bool = False,
    ) -> None:
        normalized = name.strip()
        if not normalized:
            raise ValueError("O nome do componente não pode estar vazio.")
        if normalized in self._probes and not replace:
            raise ValueError(f"Probe já registrado: {normalized}")
        self._probes[normalized] = probe

    def check(self) -> HealthReport:
        components: list[ComponentHealth] = []

        for name in sorted(self._probes):
            probe = self._probes[name]
            try:
                healthy = bool(probe())
            except Exception as error:
                components.append(
                    ComponentHealth(
                        name=name,
                        status=HealthStatus.UNHEALTHY,
                        message=str(error) or error.__class__.__name__,
                    )
                )
                continue

            components.append(
                ComponentHealth(
                    name=name,
                    status=(
                        HealthStatus.HEALTHY
                        if healthy
                        else HealthStatus.DEGRADED
                    ),
                    message="ok" if healthy else "indisponível",
                )
            )

        if any(
            component.status is HealthStatus.UNHEALTHY
            for component in components
        ):
            status = HealthStatus.UNHEALTHY
        elif any(
            component.status is HealthStatus.DEGRADED
            for component in components
        ):
            status = HealthStatus.DEGRADED
        else:
            status = HealthStatus.HEALTHY

        return HealthReport(
            status=status,
            components=tuple(components),
        )
