from __future__ import annotations

import logging

from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.planner.ai_planner import AIPlanner
from ubuntu_ai.planner.rule_planner import RulePlanner
from ubuntu_ai.tools.selection import ToolSelectionEngine

logger = logging.getLogger("ubuntu_ai.planner")


class Planner:
    """Orquestra as estratégias disponíveis para criação de planos."""

    def __init__(
        self,
        rule_planner: RulePlanner | None = None,
        ai_planner: AIPlanner | None = None,
        tool_selector: ToolSelectionEngine | None = None,
    ) -> None:
        self._rule_planner = rule_planner or RulePlanner()
        self._ai_planner = ai_planner
        self._tool_selector = tool_selector

    def create_plan(
        self,
        request: str,
        context: ContextSnapshot | None = None,
    ) -> Plan:
        normalized_request = request.strip()

        if not normalized_request:
            logger.warning("Solicitação de planejamento vazia.")
            raise ValueError("A solicitação não pode estar vazia.")

        logger.info(
            "Iniciando planejamento.",
            extra={
                "request": normalized_request,
            },
        )

        rule_plan = self._rule_planner.try_create_plan(normalized_request)

        if rule_plan is not None:
            logger.info(
                "Plano criado pelo RulePlanner.",
                extra={
                    "steps": len(rule_plan.steps),
                    "risk": rule_plan.risk.value,
                },
            )
            return self._select_tools(
                rule_plan,
                normalized_request,
                context,
            )

        if self._ai_planner is not None:
            logger.info("Delegando planejamento para AIPlanner.")

            plan = self._ai_planner.create_plan(
                normalized_request,
                context=context,
            )

            logger.info(
                "Plano criado pelo AIPlanner.",
                extra={
                    "steps": len(plan.steps),
                    "risk": plan.risk.value,
                },
            )

            return self._select_tools(
                plan,
                normalized_request,
                context,
            )

        logger.error(
            "Nenhum planejador conseguiu atender a solicitação."
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

        selected_plan = self._tool_selector.select_plan(
            plan,
            request=request,
            project_name=project_name,
        )

        logger.info(
            "Ferramentas selecionadas para o plano.",
            extra={
                "steps": len(selected_plan.steps),
            },
        )

        return selected_plan
