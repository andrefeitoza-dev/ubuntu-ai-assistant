from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.services.shell import CommandResult
from ubuntu_ai.tools.registry import ToolRegistry


class Executor:
    """Executa as etapas de um plano por meio de ferramentas registradas."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute(self, plan: Plan) -> list[CommandResult]:
        """Executa as etapas em ordem e interrompe na primeira falha."""

        shell_tool = self._registry.get("shell")
        results: list[CommandResult] = []

        for step in plan.steps:
            result = shell_tool.execute(command=step.command)

            if not isinstance(result, CommandResult):
                raise TypeError("A ferramenta shell deve retornar um CommandResult.")

            results.append(result)

            if not result.success:
                break

        return results
