from ubuntu_ai.executor.models import ExecutionResult


class ControlledExecutor:
    """Executa planos de forma controlada."""

    def execute(self) -> ExecutionResult:
        """Executa a operação aprovada.

        Nesta primeira versão o executor é apenas um placeholder.
        """

        return ExecutionResult(
            success=True,
            message="Execução concluída com sucesso.",
        )
