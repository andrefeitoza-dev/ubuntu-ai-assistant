from __future__ import annotations

import logging
from contextlib import AbstractContextManager, nullcontext

from ubuntu_ai.benchmark import BenchmarkService
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.intent.models import Intent
from ubuntu_ai.planner.ai_planner import AIPlanner
from ubuntu_ai.planner.builtin import BuiltinPlanner
from ubuntu_ai.planner.rule_planner import RulePlanner
from ubuntu_ai.tools.selection import ToolSelectionEngine

logger = logging.getLogger("ubuntu_ai.planner")


class Planner:
    """Orquestra as estratégias disponíveis para criação de planos."""

    def __init__(
        self,
        builtin_planner: BuiltinPlanner | None = None,
        rule_planner: RulePlanner | None = None,
        ai_planner: AIPlanner | None = None,
        tool_selector: ToolSelectionEngine | None = None,
        benchmark_service: BenchmarkService | None = None,
    ) -> None:
        self._builtin_planner = builtin_planner or BuiltinPlanner()
        self._rule_planner = rule_planner or RulePlanner()
        self._ai_planner = ai_planner
        self._tool_selector = tool_selector
        self._benchmark_service = benchmark_service

    def create_plan(
        self,
        request: str | Intent,
        context: ContextSnapshot | None = None,
    ) -> Plan:
        intent = request if isinstance(request, Intent) else None
        normalized_request = (
            intent.request if intent is not None else request
        ).strip()

        if not normalized_request:
            logger.warning("Solicitação de planejamento vazia.")
            raise ValueError("A solicitação não pode estar vazia.")

        with self._measurement("planner"):
            return self._create_plan(
                normalized_request,
                context,
                intent,
            )

    def _create_plan(
        self,
        request: str,
        context: ContextSnapshot | None,
        intent: Intent | None,
    ) -> Plan:
        logger.info(
            "Iniciando planejamento.",
            extra={
                "request": request,
                "intent_category": (
                    intent.category.value if intent else None
                ),
                "intent_goal": (
                    intent.goal.value if intent else None
                ),
            },
        )

        #
        # 1) Builtin Planner
        #
        builtin_plan = self._builtin_planner.try_create_plan(request)

        if builtin_plan is not None:
            logger.info("Plano criado pelo BuiltinPlanner.")
            return self._select_tools(
                builtin_plan,
                request,
                context,
            )

        #
        # 2) Rule Planner
        #
        rule_plan = self._rule_planner.try_create_plan(request)

        if rule_plan is not None:
            logger.info("Plano criado pelo RulePlanner.")
            return self._select_tools(
                rule_plan,
                request,
                context,
            )

        #
        # 3) AI Planner
        #
        if self._ai_planner is not None:
            logger.info("Delegando planejamento para AIPlanner.")

            plan_input: str | Intent = intent or request

            plan = self._ai_planner.create_plan(
                plan_input,
                context=context,
            )

            return self._select_tools(
                plan,
                request,
                context,
            )

        raise ValueError(
            "Ainda não sei criar um plano para essa solicitação."
        )

    def _select_tools(
        self,
        plan: Plan,
        request: str,
        context: ContextSnapshot | None,
    ) -> Plan:
        if self._tool_selector is None:
            return plan

        project_name = (
            context.project_name
            if context is not None
            else None
        )

        return self._tool_selector.select_plan(
            plan,
            request=request,
            project_name=project_name,
        )

    def _measurement(
        self,
        operation: str,
    ) -> AbstractContextManager[object]:
        if self._benchmark_service is None:
            return nullcontext()

        return self._benchmark_service.measure(operation)