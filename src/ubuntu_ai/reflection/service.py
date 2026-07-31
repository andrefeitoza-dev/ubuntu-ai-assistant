from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.execution.models import ExecutionResult
from ubuntu_ai.reflection.analyzer import ReflectionAnalyzer
from ubuntu_ai.reflection.models import ReflectionReport


class ReflectionService:
    def __init__(self, analyzer: ReflectionAnalyzer | None = None) -> None:
        self._analyzer = analyzer or ReflectionAnalyzer()

    def reflect_on_plan(self, plan: Plan) -> ReflectionReport:
        return self._analyzer.analyze_plan(plan)

    def reflect_on_execution(
        self,
        *,
        command: str,
        result: ExecutionResult,
        step_index: int | None = None,
    ) -> ReflectionReport:
        return self._analyzer.analyze_execution(
            command=command,
            result=result,
            step_index=step_index,
        )
