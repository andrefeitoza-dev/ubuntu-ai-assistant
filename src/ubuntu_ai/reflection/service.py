from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.execution.models import ExecutionResult
from ubuntu_ai.intent.models import Intent, IntentCategory
from ubuntu_ai.reflection.analyzer import ReflectionAnalyzer
from ubuntu_ai.reflection.models import (
    ReflectionFinding,
    ReflectionReport,
    ReflectionSeverity,
)


class ReflectionService:
    def __init__(self, analyzer: ReflectionAnalyzer | None = None) -> None:
        self._analyzer = analyzer or ReflectionAnalyzer()

    def reflect_on_plan(
        self,
        plan: Plan,
        *,
        intent: Intent | None = None,
    ) -> ReflectionReport:
        report = self._analyzer.analyze_plan(plan)
        if intent is None:
            return report

        findings = list(report.findings)
        if intent.category is IntentCategory.UNKNOWN:
            findings.append(
                ReflectionFinding(
                    code="unknown-intent",
                    message="A intenção foi classificada como desconhecida.",
                    severity=ReflectionSeverity.WARNING,
                    recommendation="Revise o objetivo antes de executar alterações.",
                )
            )
        if intent.confidence < 0.5:
            findings.append(
                ReflectionFinding(
                    code="low-intent-confidence",
                    message=(
                        "A confiança da classificação da intenção é baixa "
                        f"({intent.confidence:.2f})."
                    ),
                    severity=ReflectionSeverity.WARNING,
                    recommendation="Solicite esclarecimentos ou gere um plano conservador.",
                )
            )
        if intent.requires_confirmation and not plan.steps:
            findings.append(
                ReflectionFinding(
                    code="confirmation-without-steps",
                    message="A intenção exige confirmação, mas o plano não possui etapas.",
                    severity=ReflectionSeverity.CRITICAL,
                    recommendation="Gere novamente o plano antes de confirmar.",
                )
            )

        return ReflectionReport(
            phase=report.phase,
            findings=tuple(findings),
            score=self._score(findings),
        )

    def reflect_on_execution(
        self,
        *,
        command: str,
        result: ExecutionResult,
        step_index: int | None = None,
        intent: Intent | None = None,
    ) -> ReflectionReport:
        report = self._analyzer.analyze_execution(
            command=command,
            result=result,
            step_index=step_index,
        )
        if intent is None:
            return report
        return report

    @staticmethod
    def _score(findings: list[ReflectionFinding]) -> float:
        penalty = 0.0
        for finding in findings:
            if finding.severity is ReflectionSeverity.CRITICAL:
                penalty += 0.5
            elif finding.severity is ReflectionSeverity.WARNING:
                penalty += 0.2
        return max(0.0, round(1.0 - penalty, 2))
