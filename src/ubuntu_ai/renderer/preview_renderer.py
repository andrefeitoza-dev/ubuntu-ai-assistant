from ubuntu_ai.executor.preview import ExecutionPreview


class PreviewRenderer:
    """Transforma uma prévia de execução em texto para apresentação."""

    def render(self, preview: ExecutionPreview) -> str:
        """Retorna uma representação textual da prévia."""

        risk_name = preview.risk.name

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
            risk_name,
            "",
            "Tempo estimado:",
            f"{preview.estimated_seconds} segundos",
            "",
            "Etapas:",
            "",
        ]

        for step in preview.steps:
            lines.extend(
                [
                    f"{step.number}. {step.title}",
                    f"   Descrição: {step.description}",
                    f"   Comando: {step.command}",
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