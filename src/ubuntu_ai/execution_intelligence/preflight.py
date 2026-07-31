from __future__ import annotations

import os
import platform
import shutil
from itertools import zip_longest

from ubuntu_ai.execution_intelligence.discovery import DiscoveryEngine
from ubuntu_ai.execution_intelligence.models import (
    CheckSeverity,
    PreflightCheck,
    PreflightReport,
)
from ubuntu_ai.tools.capability import ToolCapability


class PreflightEngine:
    """Valida disponibilidade, plataforma, dependências, versão e elevação."""

    def __init__(self, discovery: DiscoveryEngine | None = None) -> None:
        self._discovery = discovery or DiscoveryEngine()

    def check(self, capability: ToolCapability) -> PreflightReport:
        checks: list[PreflightCheck] = []
        current_os = platform.system().lower()
        supported_systems = {
            item.lower() for item in capability.operating_systems
        }
        supported = current_os in supported_systems
        checks.append(
            PreflightCheck(
                code="operating_system",
                message=(
                    f"Sistema {current_os} suportado."
                    if supported
                    else f"Sistema {current_os} não suportado por {capability.name}."
                ),
                passed=supported,
                recommendation="Use uma ferramenta compatível com este sistema.",
            )
        )

        discovered = self._discovery.discover_capability(capability)
        available = [item for item in discovered if item.available]
        checks.append(
            PreflightCheck(
                code="executable",
                message=(
                    f"Executável disponível: {available[0].executable}."
                    if available
                    else (
                        f"Nenhum executável de {capability.name} "
                        "foi encontrado no PATH."
                    )
                ),
                passed=bool(available),
                recommendation=f"Instale ou habilite {capability.name} no PATH.",
            )
        )

        for dependency in capability.dependencies:
            found = shutil.which(dependency) is not None
            checks.append(
                PreflightCheck(
                    code=f"dependency:{dependency}",
                    message=(
                        f"Dependência disponível: {dependency}."
                        if found
                        else f"Dependência ausente: {dependency}."
                    ),
                    passed=found,
                    recommendation=f"Instale a dependência {dependency}.",
                )
            )

        if capability.minimum_version and available:
            version = available[0].version
            compatible = version is not None and self._version_at_least(
                version, capability.minimum_version
            )
            checks.append(
                PreflightCheck(
                    code="minimum_version",
                    message=(
                        f"Versão {version} atende ao mínimo "
                        f"{capability.minimum_version}."
                        if compatible
                        else (
                            f"Não foi possível confirmar versão mínima "
                            f"{capability.minimum_version} para {capability.name}."
                        )
                    ),
                    passed=compatible,
                    severity=CheckSeverity.WARNING,
                    recommendation=f"Atualize {capability.name} se necessário.",
                )
            )

        if capability.requires_elevation:
            elevation_available = self._is_root() or shutil.which("sudo") is not None
            checks.append(
                PreflightCheck(
                    code="elevation",
                    message=(
                        "Elevação disponível."
                        if elevation_available
                        else "A operação pode exigir privilégios administrativos."
                    ),
                    passed=elevation_available,
                    severity=CheckSeverity.WARNING,
                    recommendation="Execute com uma conta autorizada ou instale sudo.",
                )
            )

        return PreflightReport(tool_name=capability.name, checks=tuple(checks))

    @staticmethod
    def _is_root() -> bool:
        return hasattr(os, "geteuid") and os.geteuid() == 0

    @staticmethod
    def _version_at_least(current: str, minimum: str) -> bool:
        def parts(value: str) -> tuple[int, ...]:
            return tuple(int(item) for item in value.split(".") if item.isdigit())

        current_parts = parts(current)
        minimum_parts = parts(minimum)
        for current_item, minimum_item in zip_longest(
            current_parts, minimum_parts, fillvalue=0
        ):
            if current_item != minimum_item:
                return current_item > minimum_item
        return True
