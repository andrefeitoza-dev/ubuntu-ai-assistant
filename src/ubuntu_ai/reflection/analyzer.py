from __future__ import annotations

from collections import Counter
from shlex import join

from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.execution.models import ExecutionResult, ExecutionStatus
from ubuntu_ai.reflection.models import (
    ReflectionFinding,
    ReflectionPhase,
    ReflectionReport,
    ReflectionSeverity,
)


class ReflectionAnalyzer:
    """Rule-based analysis for plans and execution outcomes."""

    _DESTRUCTIVE_TOKENS = {"rm", "mkfs", "fdisk", "parted", "shutdown", "reboot", "poweroff"}

    def analyze_plan(self, plan: Plan) -> ReflectionReport:
        findings: list[ReflectionFinding] = []
        commands = [join(step.command) for step in plan.steps]

        if not plan.steps:
            findings.append(
                ReflectionFinding(
                    code="empty-plan",
                    message="O plano não possui etapas executáveis.",
                    severity=ReflectionSeverity.CRITICAL,
                    recommendation="Revise o objetivo e gere um novo plano.",
                )
            )

        duplicates = {command for command, count in Counter(commands).items() if count > 1}
        for command in sorted(duplicates):
            findings.append(
                ReflectionFinding(
                    code="duplicate-command",
                    message=f"O comando '{command}' aparece mais de uma vez no plano.",
                    severity=ReflectionSeverity.WARNING,
                    recommendation="Remova etapas redundantes antes da execução.",
                )
            )

        for index, step in enumerate(plan.steps):
            if not step.command:
                findings.append(
                    ReflectionFinding(
                        code="empty-command",
                        message=f"A etapa {index + 1} não possui comando.",
                        severity=ReflectionSeverity.CRITICAL,
                        step_index=index,
                    )
                )
                continue
            executable = step.command[0].lower()
            if executable in self._DESTRUCTIVE_TOKENS and plan.risk is RiskLevel.LOW:
                findings.append(
                    ReflectionFinding(
                        code="risk-mismatch",
                        message=(
                            f"A etapa {index + 1} usa '{executable}', mas o plano "
                            "foi classificado como baixo risco."
                        ),
                        severity=ReflectionSeverity.CRITICAL,
                        step_index=index,
                        recommendation="Reavalie o risco e exija confirmação reforçada.",
                    )
                )
            if step.tool_name is None:
                findings.append(
                    ReflectionFinding(
                        code="tool-not-selected",
                        message=f"A etapa {index + 1} não possui ferramenta selecionada.",
                        severity=ReflectionSeverity.WARNING,
                        step_index=index,
                        recommendation="Execute novamente o Tool Selection Engine.",
                    )
                )

        return ReflectionReport(
            phase=ReflectionPhase.PLAN,
            findings=tuple(findings),
            score=self._score(findings),
        )

    def analyze_execution(
        self,
        *,
        command: str,
        result: ExecutionResult,
        step_index: int | None = None,
    ) -> ReflectionReport:
        findings: list[ReflectionFinding] = []

        if result.status is ExecutionStatus.EXECUTED:
            findings.append(
                ReflectionFinding(
                    code="execution-succeeded",
                    message=f"O comando '{command}' foi executado com sucesso.",
                    step_index=step_index,
                )
            )
        elif result.status is ExecutionStatus.BLOCKED:
            findings.append(
                ReflectionFinding(
                    code="execution-blocked",
                    message=f"O comando '{command}' foi bloqueado: {result.message}",
                    severity=ReflectionSeverity.WARNING,
                    step_index=step_index,
                    recommendation="Corrija o preflight ou gere uma alternativa segura.",
                )
            )
        else:
            details = result.stderr.strip() or result.message
            findings.append(
                ReflectionFinding(
                    code="execution-failed",
                    message=f"O comando '{command}' falhou: {details}",
                    severity=ReflectionSeverity.WARNING,
                    step_index=step_index,
                    recommendation="Verifique saída, permissões e pré-requisitos antes de repetir.",
                )
            )
            if result.return_code in {126, 127}:
                findings.append(
                    ReflectionFinding(
                        code="command-unavailable",
                        message="A falha indica comando indisponível ou não executável.",
                        severity=ReflectionSeverity.CRITICAL,
                        step_index=step_index,
                        recommendation="Descubra uma ferramenta disponível e replaine a etapa.",
                    )
                )

        return ReflectionReport(
            phase=ReflectionPhase.EXECUTION,
            findings=tuple(findings),
            score=self._score(findings),
        )

    @staticmethod
    def _score(findings: list[ReflectionFinding]) -> float:
        penalty = 0.0
        for finding in findings:
            if finding.severity is ReflectionSeverity.CRITICAL:
                penalty += 0.5
            elif finding.severity is ReflectionSeverity.WARNING:
                penalty += 0.2
            else:
                penalty += 0.0
        return max(0.0, round(1.0 - penalty, 2))
