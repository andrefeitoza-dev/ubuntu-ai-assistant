from ubuntu_ai.executor.preview import ExecutionPreview
from ubuntu_ai.renderer.command_formatter import CommandFormatter


class PreviewRenderer:
    """Transforma uma prévia de execução em texto para apresentação."""

    def __init__(
        self,
        command_formatter: CommandFormatter | None = None,
    ) -> None:
        self._command_formatter = command_formatter or CommandFormatter()

    def render(self, preview: ExecutionPreview) -> str:
        """Retorna uma representação textual da prévia."""

        lines = [
            "=" * 50,
            "Ubuntu AI Assistant",
            "Execution Preview (DRY RUN)",
            "=" * 50,
            "",
            "Objetivo:",
            preview.goal,
            "",
            "Risco:",
            preview.risk.name,
            "",
            "Tempo estimado:",
            f"{preview.estimated_seconds} segundos",
            "",
            "Etapas:",
            "",
        ]

        for step in preview.steps:
            formatted_command = self._command_formatter.format(step.command)

            lines.extend(
                [
                    f"{step.number}. {step.title}",
                    f"   Descrição: {step.description}",
                    f"   Comando: {formatted_command}",
                    "",
                ]
            )

        lines.extend(
            [
                "-" * 50,
                "Nenhuma alteração será realizada.",
                "Modo de simulação ativo.",
            ]
        )

        return "\n".join(lines)
