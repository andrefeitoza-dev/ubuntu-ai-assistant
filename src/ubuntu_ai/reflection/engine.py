from contextlib import AbstractContextManager, nullcontext

from ubuntu_ai.benchmark import BenchmarkService
from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.execution.models import ExecutionResult
from ubuntu_ai.intent.models import Intent
from ubuntu_ai.reflection.models import ReflectionReport
from ubuntu_ai.reflection.service import ReflectionService


class ReflectionEngine:
    """Facade used by the runtime to perform pre and post execution reflection."""

    def __init__(
        self,
        service: ReflectionService | None = None,
        benchmark_service: BenchmarkService | None = None,
    ) -> None:
        self._service = service or ReflectionService()
        self._benchmark_service = benchmark_service

    def before_execution(
        self,
        plan: Plan,
        *,
        intent: Intent | None = None,
    ) -> ReflectionReport:
        with self._measurement("reflection"):
            return self._service.reflect_on_plan(plan, intent=intent)

    def after_execution(
        self,
        *,
        command: str,
        result: ExecutionResult,
        step_index: int | None = None,
        intent: Intent | None = None,
    ) -> ReflectionReport:
        with self._measurement("reflection"):
            return self._service.reflect_on_execution(
                command=command,
                result=result,
                step_index=step_index,
                intent=intent,
            )

    def _measurement(self, operation: str) -> AbstractContextManager[object]:
        if self._benchmark_service is None:
            return nullcontext()
        return self._benchmark_service.measure(operation)
