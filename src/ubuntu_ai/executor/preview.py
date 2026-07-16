from dataclasses import dataclass

from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.domain.risk import RiskLevel


@dataclass(frozen=True, slots=True)
class PreviewStep:
    """Representa uma etapa exibida no modo de simulação."""

    number: int
    title: str
    description: str
    command: list[str]


@dataclass(frozen=True, slots=True)
class ExecutionPreview:
    """Prévia de execução que não altera o sistema."""

    goal: str
    risk: RiskLevel
    estimated_seconds: int
    steps: tuple[PreviewStep, ...]
    dry_run: bool = True


class PreviewBuilder:
    """Converte um plano em uma prévia segura de execução."""

    def build(self, plan: Plan) -> ExecutionPreview:
        steps = tuple(
            PreviewStep(
                number=index,
                title=step.title,
                description=step.description,
                command=step.command.copy(),
            )
            for index, step in enumerate(plan.steps, start=1)
        )

        return ExecutionPreview(
            goal=plan.goal,
            risk=plan.risk,
            estimated_seconds=plan.estimated_seconds,
            steps=steps,
        )