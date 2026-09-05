import json
from contextlib import AbstractContextManager, nullcontext

from ubuntu_ai.ai import AIProvider, AIRequest
from ubuntu_ai.ai.prompt_builder import PlanningPromptBuilder
from ubuntu_ai.benchmark import BenchmarkService
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.decision.engine import DecisionEngine
from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.intent.context import IntentContextBuilder
from ubuntu_ai.intent.models import Intent
from ubuntu_ai.knowledge.service import KnowledgeService
from ubuntu_ai.learning.service import LearningService
from ubuntu_ai.memory_intelligence.models import MemorySelection
from ubuntu_ai.planner.advisor import PlanningAdvisor
from ubuntu_ai.semantic.service import RAGContextBuilder


class AIPlanner:
    """Cria planos estruturados usando um provedor de IA."""

    def __init__(
        self,
        provider: AIProvider,
        prompt_builder: PlanningPromptBuilder | None = None,
        knowledge_service: KnowledgeService | None = None,
        learning_service: LearningService | None = None,
        rag_context_builder: RAGContextBuilder | None = None,
        benchmark_service: BenchmarkService | None = None,
        intent_context_builder: IntentContextBuilder | None = None,
        planning_advisor: PlanningAdvisor | None = None,
        decision_engine: DecisionEngine | None = None,
    ) -> None:
        self._provider = provider
        self._prompt_builder = prompt_builder or PlanningPromptBuilder()
        self._knowledge_service = knowledge_service
        self._learning_service = learning_service
        self._rag_context_builder = rag_context_builder
        self._benchmark_service = benchmark_service
        self._intent_context_builder = intent_context_builder or IntentContextBuilder()
        self._planning_advisor = planning_advisor or PlanningAdvisor()
        self._decision_engine = decision_engine or DecisionEngine()

    def create_plan(
        self,
        request: str | Intent,
        context: ContextSnapshot | None = None,
        memory: MemorySelection | None = None,
    ) -> Plan:
        intent = request if isinstance(request, Intent) else None
        normalized_request = (intent.request if intent is not None else request).strip()
        if not normalized_request:
            raise ValueError("A solicitação não pode estar vazia.")

        response = self._provider.generate(
            AIRequest(
                prompt=self._build_prompt(
                    normalized_request,
                    context,
                    intent,
                    memory,
                )
            )
        )
        return self._parse_plan(response.content)

    def _build_prompt(
        self,
        request: str,
        context: ContextSnapshot | None = None,
        intent: Intent | None = None,
        memory: MemorySelection | None = None,
    ) -> str:
        knowledge_context = self._knowledge_context(request, intent)
        learning_context = self._learning_context(request, context, intent)
        memory_context = (
            memory.to_prompt() if memory is not None and not memory.is_empty() else None
        )
        intent_context = (
            self._intent_context_builder.prompt_context(intent) if intent is not None else None
        )
        planning_profile = self._planning_advisor.build(context)
        planning_advice = None if planning_profile.is_empty() else planning_profile.to_prompt()
        decision_context = self._decision_engine.decide(planning_profile).to_prompt()

        return self._prompt_builder.build(
            request=request,
            context=context,
            knowledge_context=knowledge_context,
            learning_context=learning_context,
            memory_context=memory_context,
            intent_context=intent_context,
            planning_advice=planning_advice,
            decision_context=decision_context,
        )

    def _knowledge_context(
        self,
        request: str,
        intent: Intent | None,
    ) -> str | None:
        query = self._intent_context_builder.search_query(intent) if intent is not None else request
        if self._rag_context_builder is not None:
            with self._measurement("knowledge"):
                return self._rag_context_builder.build(
                    query,
                    limit=3,
                    max_chars=1_500,
                )
        if self._knowledge_service is None:
            return None
        with self._measurement("knowledge"):
            results = (
                self._knowledge_service.search_for_intent(intent, limit=3)
                if intent is not None
                else self._knowledge_service.search(request, limit=3)
            )
        if not results:
            return None
        return "\n".join(f"- {result.document.title}: {result.excerpt}" for result in results)

    def _learning_context(
        self,
        request: str,
        context: ContextSnapshot | None,
        intent: Intent | None,
    ) -> str | None:
        if self._learning_service is None:
            return None
        project_name = context.project_name if context is not None else None
        with self._measurement("learning"):
            context_text = (
                self._learning_service.context_for_intent(
                    intent,
                    project_name=project_name,
                    limit=3,
                )
                if intent is not None
                else self._learning_service.context_for_prompt(
                    request,
                    project_name=project_name,
                    limit=3,
                )
            )
        if context_text is None:
            return None
        return context_text[:1_000]

    def _measurement(
        self,
        operation: str,
    ) -> AbstractContextManager[object]:
        if self._benchmark_service is None:
            return nullcontext()
        return self._benchmark_service.measure(operation)

    def _parse_plan(self, content: str) -> Plan:
        try:
            data = json.loads(content)
        except json.JSONDecodeError as error:
            raise ValueError("A IA retornou um plano com JSON inválido.") from error

        try:
            goal = data["goal"]
            estimated_seconds = data["estimated_seconds"]
            risk = RiskLevel(data["risk"])
            raw_steps = data["steps"]
        except (KeyError, TypeError, ValueError) as error:
            raise ValueError("A IA retornou um plano com estrutura inválida.") from error

        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("A IA retornou um objetivo inválido.")
        if not isinstance(estimated_seconds, int) or estimated_seconds <= 0:
            raise ValueError("A IA retornou um tempo estimado inválido.")
        if not isinstance(raw_steps, list) or not raw_steps:
            raise ValueError("A IA retornou etapas inválidas.")

        plan = Plan(
            goal=goal.strip(),
            estimated_seconds=estimated_seconds,
            risk=risk,
            planner="ai",
        )
        for raw_step in raw_steps:
            plan.add_step(self._parse_step(raw_step))
        return plan

    def _parse_step(self, raw_step: object) -> PlanStep:
        if not isinstance(raw_step, dict):
            raise ValueError("A IA retornou uma etapa inválida.")

        title = raw_step.get("title")
        description = raw_step.get("description")
        command = raw_step.get("command")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("A IA retornou um título de etapa inválido.")
        if not isinstance(description, str) or not description.strip():
            raise ValueError("A IA retornou uma descrição de etapa inválida.")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(item, str) and item for item in command)
        ):
            raise ValueError("A IA retornou um comando de etapa inválido.")

        return PlanStep(
            title=title.strip(),
            description=description.strip(),
            command=command,
        )
