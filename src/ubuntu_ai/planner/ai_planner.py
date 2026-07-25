import json

from ubuntu_ai.ai import AIProvider, AIRequest
from ubuntu_ai.context.models import ContextSnapshot
from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel


class AIPlanner:
    """Cria planos estruturados usando um provedor de IA."""

    def __init__(self, provider: AIProvider) -> None:
        self._provider = provider

    def create_plan(
        self,
        request: str,
        context: ContextSnapshot | None = None,
    ) -> Plan:
        normalized_request = request.strip()

        if not normalized_request:
            raise ValueError("A solicitação não pode estar vazia.")

        response = self._provider.generate(
            AIRequest(prompt=self._build_prompt(normalized_request, context))
        )

        return self._parse_plan(response.content)

    def _build_prompt(
        self,
        request: str,
        context: ContextSnapshot | None = None,
    ) -> str:
        context_section = (
            f"Contexto disponível:\n{context.to_prompt()}\n"
            if context is not None
            else ""
        )

        return (
            "Crie um plano seguro para Ubuntu em JSON válido.\n"
            f"{context_section}"
            "Use exatamente esta estrutura:\n"
            "{\n"
            '  "goal": "objetivo",\n'
            '  "estimated_seconds": 120,\n'
            '  "risk": "low|medium|high|critical",\n'
            '  "steps": [\n'
            "    {\n"
            '      "title": "etapa",\n'
            '      "description": "descrição",\n'
            '      "command": ["comando", "argumento"]\n'
            "    }\n"
            "  ]\n"
            "}\n"
            "Não inclua Markdown nem explicações fora do JSON.\n"
            f"Solicitação: {request}"
        )

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