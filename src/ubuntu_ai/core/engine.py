from ubuntu_ai.core.intent import Intent
from ubuntu_ai.explainer.explainer import Explainer
from ubuntu_ai.planner.planner import Planner


class CoreEngine:
    """Responsável por orquestrar o fluxo principal do Ubuntu AI Assistant."""

    def __init__(self) -> None:
        self._planner = Planner()
        self._explainer = Explainer()

    def detect_intent(self, text: str) -> Intent:
        text = text.lower()

        if "doctor" in text:
            return Intent.DOCTOR

        if "explique" in text:
            return Intent.EXPLAIN

        if "instale" in text or "configure" in text:
            return Intent.PLAN

        return Intent.CHAT

    def process(self, request: str) -> str:
        """Processa uma solicitação do usuário."""

        intent = self.detect_intent(request)

        if intent == Intent.PLAN:
            plan = self._planner.create_plan(request)
            return self._explainer.explain(plan)

        if intent == Intent.DOCTOR:
            return "Executar Doctor"

        if intent == Intent.EXPLAIN:
            return "Modo Explain"

        return "Modo Chat"