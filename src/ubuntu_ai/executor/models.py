from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """Resultado produzido por uma execução controlada."""

    success: bool
    message: str