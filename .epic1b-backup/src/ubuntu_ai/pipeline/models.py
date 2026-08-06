from dataclasses import dataclass

from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.executor.preview import ExecutionPreview


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Resultado completo produzido pelo pipeline de execução."""

    plan: Plan
    preview: ExecutionPreview
    rendered_preview: str