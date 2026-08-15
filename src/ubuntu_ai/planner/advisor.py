from __future__ import annotations

from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.planner.models import PlanningProfile


class PlanningAdvisor:
    """Analisa o ambiente e produz um perfil estruturado de planejamento."""

    def build(
        self,
        context: ContextSnapshot | None,
    ) -> PlanningProfile:
        if context is None:
            return PlanningProfile()

        environment = context.environment

        profiles: list[str] = []
        recommendations: list[str] = []
        risk_hints: list[str] = []
        preferred_tools: list[str] = []

        if environment is not None:
            if environment.project_name:
                profiles.append("Project Environment")

            if environment.git_repository:
                profiles.append("Git Repository")
                recommendations.append("Preserve o histórico Git e evite operações destrutivas.")
                preferred_tools.append("git")

            if environment.python_version:
                profiles.append("Python Project")
                preferred_tools.extend(
                    [
                        "python",
                        "pytest",
                        "ruff",
                    ]
                )

            if environment.virtual_environment:
                recommendations.append("Utilize o ambiente virtual existente.")

            if environment.docker_available:
                profiles.append("Docker Ready")
                recommendations.append("Prefira containers Docker quando apropriado.")
                preferred_tools.append("docker")

            if environment.ollama_available:
                profiles.append("Local AI Ready")
                recommendations.append("Considere utilizar modelos locais via Ollama.")
                preferred_tools.append("ollama")

        if context.last_errors:
            risk_hints.append("Existem falhas recentes registradas no contexto.")
            recommendations.append("Evite repetir comandos que falharam recentemente.")

        if context.last_commands:
            recommendations.append("Considere os comandos executados anteriormente.")

        return PlanningProfile(
            profiles=tuple(dict.fromkeys(profiles)),
            recommendations=tuple(dict.fromkeys(recommendations)),
            risk_hints=tuple(dict.fromkeys(risk_hints)),
            preferred_tools=tuple(dict.fromkeys(preferred_tools)),
        )
