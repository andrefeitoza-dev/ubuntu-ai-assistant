from __future__ import annotations

from collections.abc import Callable

from ubuntu_ai.runtime_integration.models import (
    RuntimeCycleResult,
    RuntimeRequest,
)
from ubuntu_ai.runtime_integration.workflow import RuntimeWorkflow


class MultiAgentRuntime:
    """Fachada de alto nível para o novo runtime multiagente."""

    def __init__(self, workflow: RuntimeWorkflow) -> None:
        self._workflow = workflow

    def run(
        self,
        request: RuntimeRequest,
        *,
        execution_action: Callable[[object], object] | None = None,
    ) -> RuntimeCycleResult:
        return self._workflow.run(
            request,
            execution_action=execution_action,
        )
