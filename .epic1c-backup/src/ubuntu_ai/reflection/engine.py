from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.execution.models import ExecutionResult
from ubuntu_ai.reflection.models import ReflectionReport
from ubuntu_ai.reflection.service import ReflectionService


class ReflectionEngine:
    """Facade used by the runtime to perform pre and post execution reflection."""

    def __init__(self, service: ReflectionService | None = None) -> None:
        self._service = service or ReflectionService()

    def before_execution(self, plan: Plan) -> ReflectionReport:
        return self._service.reflect_on_plan(plan)

    def after_execution(
        self,
        *,
        command: str,
        result: ExecutionResult,
        step_index: int | None = None,
    ) -> ReflectionReport:
        return self._service.reflect_on_execution(
            command=command,
            result=result,
            step_index=step_index,
        )
