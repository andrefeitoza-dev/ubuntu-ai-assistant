from __future__ import annotations

from ubuntu_ai.agent.models import AgentResult, AgentTask
from ubuntu_ai.agent.runtime import AgentRuntime
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.execution.models import ExecutionStatus

from .models import (
    AgentLoopConfig,
    IterationRecord,
    LoopEvent,
    LoopSnapshot,
    LoopState,
    StopReason,
)
from .replanner import AgentReplanner
from .watchdog import LoopWatchdog


class AgentLoopController:
    """Coordena execução iterativa sem remover a confirmação humana."""

    def __init__(
        self,
        runtime: AgentRuntime,
        replanner: AgentReplanner | None = None,
        config: AgentLoopConfig | None = None,
        watchdog: LoopWatchdog | None = None,
    ) -> None:
        self._runtime = runtime
        self._replanner = replanner or AgentReplanner()
        self._config = config or AgentLoopConfig()
        self._watchdog = watchdog or LoopWatchdog(self._config.max_stalled_iterations)
        self._goal = ""
        self._state = LoopState.IDLE
        self._iteration = 0
        self._pending_plan: AgentResult | None = None
        self._pending_request: str | None = None
        self._records: list[IterationRecord] = []
        self._events: list[LoopEvent] = []
        self._stop_reason: StopReason | None = None
        self._cycle_generation = 0

    def start(self, goal: str) -> LoopSnapshot:
        clean_goal = goal.strip()
        if not clean_goal:
            raise ValueError("O objetivo não pode estar vazio.")
        if self._state not in {
            LoopState.IDLE,
            LoopState.COMPLETED,
            LoopState.BLOCKED,
            LoopState.FAILED,
            LoopState.CANCELLED,
        }:
            raise RuntimeError("Já existe um ciclo de agente em andamento.")

        self._cycle_generation += 1
        generation = self._cycle_generation
        self._goal = clean_goal
        self._state = LoopState.IDLE
        self._iteration = 0
        self._pending_plan = None
        self._pending_request = None
        self._records.clear()
        self._events.clear()
        self._stop_reason = None
        self._watchdog.reset()
        return self._plan(clean_goal, generation)

    def confirm(self) -> LoopSnapshot:
        if self._state is not LoopState.WAITING_CONFIRMATION:
            raise RuntimeError("O ciclo não está aguardando confirmação.")
        if self._pending_plan is None or self._pending_request is None:
            raise RuntimeError("Não existe plano pendente.")

        self._transition(LoopState.EXECUTING, "Execução da iteração confirmada.")
        results = self._runtime.confirm()
        self._records.append(
            IterationRecord(
                number=self._iteration,
                request=self._pending_request,
                plan_result=self._pending_plan,
                execution_results=results,
            )
        )
        self._pending_plan = None
        self._pending_request = None

        if any(result.status is ExecutionStatus.BLOCKED for result in results):
            return self._stop(
                LoopState.BLOCKED,
                StopReason.EXECUTION_BLOCKED,
                "A política de segurança ou o preflight bloqueou a execução.",
            )

        if results and all(
            result.status in {ExecutionStatus.APPROVED, ExecutionStatus.EXECUTED}
            for result in results
        ):
            return self._stop(
                LoopState.COMPLETED,
                StopReason.GOAL_REACHED,
                "A iteração foi concluída com sucesso.",
            )

        if self._watchdog.observe(results):
            return self._stop(
                LoopState.FAILED,
                StopReason.NO_PROGRESS,
                "O watchdog detectou repetição sem progresso.",
            )

        if self._iteration >= self._config.max_iterations:
            return self._stop(
                LoopState.FAILED,
                StopReason.MAX_ITERATIONS,
                "O limite máximo de iterações foi atingido.",
            )

        self._transition(LoopState.REPLANNING, "Replanejamento após falha.")
        request = self._replanner.build_request(
            goal=self._goal,
            iteration=self._iteration,
            results=results,
        )
        return self._plan(request, self._cycle_generation)

    def cancel(self) -> LoopSnapshot:
        if self._state not in {
            LoopState.WAITING_CONFIRMATION,
            LoopState.PLANNING,
            LoopState.REPLANNING,
        }:
            raise RuntimeError("O ciclo atual não pode ser cancelado.")
        self._pending_plan = None
        self._pending_request = None
        return self._stop(
            LoopState.CANCELLED,
            StopReason.USER_CANCELLED,
            "Ciclo cancelado pelo usuário.",
        )

    def snapshot(self) -> LoopSnapshot:
        return LoopSnapshot(
            goal=self._goal,
            state=self._state,
            iteration=self._iteration,
            pending_plan=self._pending_plan,
            records=tuple(self._records),
            events=tuple(self._events),
            stop_reason=self._stop_reason,
        )

    def _plan(self, request: str, generation: int) -> LoopSnapshot:
        if self._iteration >= self._config.max_iterations:
            return self._stop(
                LoopState.FAILED,
                StopReason.MAX_ITERATIONS,
                "O limite máximo de iterações foi atingido antes do planejamento.",
            )
        self._iteration += 1
        self._transition(LoopState.PLANNING, f"Planejando iteração {self._iteration}.")
        try:
            plan = self._runtime.run(AgentTask(request=request))
        except Exception as exc:
            if generation != self._cycle_generation or self._state is LoopState.CANCELLED:
                return self.snapshot()
            return self._stop(
                LoopState.FAILED,
                StopReason.PLANNING_ERROR,
                f"Falha durante o planejamento: {exc}",
            )

        if generation != self._cycle_generation or self._state is LoopState.CANCELLED:
            return self.snapshot()

        self._pending_plan = plan
        self._pending_request = request

        if self._can_auto_execute(plan):
            self._transition(
                LoopState.WAITING_CONFIRMATION,
                "Plano de baixo risco aprovado para execução automática.",
            )
            return self.confirm()

        self._transition(
            LoopState.WAITING_CONFIRMATION,
            "Plano pronto e aguardando confirmação explícita.",
        )
        return self.snapshot()

    @staticmethod
    def _can_auto_execute(plan: AgentResult) -> bool:
        """Permite autoexecução somente para planos explicitamente LOW."""

        pipeline_result = plan.pipeline_result

        if pipeline_result is None:
            return False

        execution_plan = pipeline_result.plan

        if execution_plan is None:
            return False

        return execution_plan.risk is RiskLevel.LOW

    def _transition(self, state: LoopState, message: str) -> None:
        self._state = state
        self._events.append(LoopEvent(iteration=self._iteration, state=state, message=message))

    def _stop(
        self,
        state: LoopState,
        reason: StopReason,
        message: str,
    ) -> LoopSnapshot:
        self._stop_reason = reason
        self._transition(state, message)
        return self.snapshot()
