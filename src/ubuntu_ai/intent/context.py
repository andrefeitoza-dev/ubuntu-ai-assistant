from __future__ import annotations

from ubuntu_ai.intent.models import Intent, IntentCategory, IntentGoal


class IntentContextBuilder:
    """Converte uma intenção em consultas e contexto reutilizáveis."""

    def search_query(self, intent: Intent) -> str:
        parts = [intent.request]
        parts.extend(intent.entity_names)
        if intent.category is not IntentCategory.UNKNOWN:
            parts.append(intent.category.value)
        if intent.goal is not IntentGoal.UNKNOWN:
            parts.append(intent.goal.value)
        return " ".join(dict.fromkeys(part for part in parts if part))

    def prompt_context(self, intent: Intent) -> str:
        entities = ", ".join(intent.entity_names) or "nenhuma"
        return (
            f"Categoria: {intent.category.value}\n"
            f"Objetivo: {intent.goal.value}\n"
            f"Confiança: {intent.confidence:.2f}\n"
            f"Entidades: {entities}\n"
            f"Confirmação necessária: {'sim' if intent.requires_confirmation else 'não'}"
        )
