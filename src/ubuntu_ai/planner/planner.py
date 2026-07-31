from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.planner.ai_planner import AIPlanner
from ubuntu_ai.planner.rule_planner import RulePlanner
from ubuntu_ai.tools.selection import ToolSelectionEngine


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
            raise ValueError("A solicitação não pode estar vazia.")

        rule_plan = self._rule_planner.try_create_plan(normalized_request)

        if rule_plan is not None:
            return self._select_tools(rule_plan, normalized_request, context)

        if self._ai_planner is not None:
            plan = self._ai_planner.create_plan(normalized_request, context=context)
            return self._select_tools(plan, normalized_request, context)

        raise ValueError("Ainda não sei criar um plano para essa solicitação.")
    def _select_tools(
        self,
        plan: Plan,
        request: str,
        context: ContextSnapshot | None,
    ) -> Plan:
        if self._tool_selector is None:
            return plan
        project_name = context.project_name if context is not None else None
        return self._tool_selector.select_plan(
            plan,
            request=request,
            project_name=project_name,
        )
