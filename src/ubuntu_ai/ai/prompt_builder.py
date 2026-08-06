from __future__ import annotations

from ubuntu_ai.context.models import ContextSnapshot


class PlanningPromptBuilder:
    """Monta o prompt do planejador com contrato JSON e contexto disponível."""

    def build(
        self,
        *,
        request: str,
        context: ContextSnapshot | None = None,
        knowledge_context: str | None = None,
        learning_context: str | None = None,
        intent_context: str | None = None,
    ) -> str:
        context_section = (
            f"Contexto disponível:\n{context.to_prompt()}\n"
            if context is not None
            else ""
        )
        knowledge_section = (
            f"Conhecimento local relevante:\n{knowledge_context}\n"
            if knowledge_context
            else ""
        )
        intent_section = (
            f"Intenção estruturada:\n{intent_context}\n"
            if intent_context
            else ""
        )
        learning_section = (
            f"Aprendizado de execuções anteriores:\n{learning_context}\n"
            if learning_context
            else ""
        )
        conversation_section = ""
        if context is not None and context.conversation_history:
            conversation_section = (
                "Histórico recente da conversa:\n"
                + "\n".join(context.conversation_history)
                + "\n"
            )

        return (
            "Crie um plano seguro para Ubuntu em JSON válido.\n"
            f"{context_section}"
            f"{conversation_section}"
            f"{knowledge_section}"
            f"{intent_section}"
            f"{learning_section}"
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
            f"Solicitação atual: {request}"
        )
