from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.planner.ai_planner import AIPlanner
from ubuntu_ai.planner.rule_planner import RulePlanner


class Planner:
    """Orquestra as estratégias disponíveis para criação de planos."""

    def __init__(
        self,
        rule_planner: RulePlanner | None = None,
        ai_planner: AIPlanner | None = None,
    ) -> None:
        self._rule_planner = rule_planner or RulePlanner()
        self._ai_planner = ai_planner

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
            return rule_plan

        if self._ai_planner is not None:
            return self._ai_planner.create_plan(normalized_request, context=context)

        raise ValueError("Ainda não sei criar um plano para essa solicitação.")