from __future__ import annotations

from ubuntu_ai.execution.models import ExecutionResult


class AgentReplanner:
    """Produz uma nova solicitação mantendo o objetivo e evidências da falha."""

    def build_request(
        self,
        *,
        goal: str,
        iteration: int,
        results: tuple[ExecutionResult, ...],
    ) -> str:
        evidence = self._evidence(results)
        return (
            f"Objetivo original: {goal}\n"
            f"A tentativa {iteration} não concluiu o objetivo. "
            "Replaneje usando uma abordagem diferente, preserve as políticas "
            "de segurança e não repita comandos que falharam sem corrigir a causa.\n"
            f"Evidências da execução:\n{evidence}"
        )

    @staticmethod
    def _evidence(results: tuple[ExecutionResult, ...]) -> str:
        lines: list[str] = []
        for index, result in enumerate(results, start=1):
            detail = result.stderr.strip() or result.stdout.strip() or result.message
            lines.append(
                f"{index}. status={result.status.value}; "
                f"comando={result.command or 'não informado'}; "
                f"retorno={result.return_code}; detalhe={detail[:800]}"
            )
        return "\n".join(lines) or "Nenhum resultado foi produzido."
