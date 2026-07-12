from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.services.shell import ShellService


class Executor:
    """Executa um plano passo a passo."""

    def __init__(self) -> None:
        self._shell = ShellService()

    def execute(self, plan: Plan) -> list[str]:
        """Executa todas as etapas do plano."""

        results: list[str] = []

        for step in plan.steps:
            results.append(f"Executando: {step.title}")

        return results