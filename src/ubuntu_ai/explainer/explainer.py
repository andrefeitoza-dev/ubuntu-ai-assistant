from ubuntu_ai.domain.plan import Plan


class Explainer:
    """Explica um plano para o usuário."""

    def explain(self, plan: Plan) -> str:
        lines = [
            f"Objetivo: {plan.goal}",
            f"Risco: {plan.risk.value.upper()}",
            f"Tempo estimado: {plan.estimated_seconds} segundos",
            "",
            "Etapas:",
        ]

        for index, step in enumerate(plan.steps, start=1):
            lines.extend(
                [
                    "",
                    f"{index}. {step.title}",
                    f"Descrição: {step.description}",
                    f"Comando: {' '.join(step.command)}",
                ]
            )

        return "\n".join(lines)
