from __future__ import annotations

from ubuntu_ai.context.models import ContextSnapshot


class PlanningPromptBuilder:
    """Monta o prompt do planejador com contexto rico do ambiente."""

    def build(
        self,
        *,
        request: str,
        context: ContextSnapshot | None = None,
        knowledge_context: str | None = None,
        learning_context: str | None = None,
        memory_context: str | None = None,
        intent_context: str | None = None,
        planning_advice: str | None = None,
        decision_context: str | None = None,
    ) -> str:
        sections: list[str] = [
            "Você é o planejador do Ubuntu AI Assistant.",
            "Sua função é produzir planos seguros, determinísticos e objetivos.",
        ]

        if context is not None:
            sections.extend(["=== CONTEXTO ===", context.to_prompt()])
            if context.conversation_history:
                sections.append("Histórico recente da conversa:")
                sections.extend(context.conversation_history)

        if knowledge_context:
            sections.extend(["Conhecimento local relevante:", knowledge_context])
        if intent_context:
            sections.extend(["Intenção estruturada:", intent_context])
        if learning_context:
            sections.extend(["Aprendizado de execuções anteriores:", learning_context])
        if memory_context:
            sections.extend(["Memórias relevantes:", memory_context])
        if planning_advice:
            sections.extend(["Recomendações de planejamento:", planning_advice])
        if decision_context:
            sections.extend(["Decisão operacional:", decision_context])

        sections.append("=== REGRAS ===")
        sections.extend(
            [
                "- Utilize o contexto detectado para adaptar o plano.",
                "- Preserve o ambiente existente.",
                "- Evite comandos destrutivos.",
                "- Não invente arquivos ou diretórios.",
                "- Gere etapas pequenas e verificáveis.",
                ("- Considere Docker, Git, Python, Ollama e Virtualenv quando disponíveis."),
            ]
        )

        sections.append("Use exatamente esta estrutura:")
        sections.append(
            """
{
  "goal": "objetivo",
  "estimated_seconds": 120,
  "risk": "low|medium|high|critical",
  "steps": [
    {
      "title": "etapa",
      "description": "descrição",
      "command": ["comando", "argumento"]
    }
  ]
}
""".strip()
        )

        sections.extend(
            [
                "Não utilize Markdown.",
                "Não escreva explicações.",
                "Retorne apenas JSON válido.",
                f"Solicitação atual: {request}",
            ]
        )
        return "\n\n".join(sections)
