from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.intent.models import Intent


@dataclass(frozen=True, slots=True)
class IntentView:
    """Representação pronta para interfaces CLI e TUI."""

    request: str
    category: str
    goal: str
    confidence_percent: str
    entities: str
    requires_confirmation: str


class IntentPresenter:
    """Converte o domínio de intenção em dados de apresentação."""

    def present(self, intent: Intent) -> IntentView:
        entities = ", ".join(intent.entity_names) or "—"
        return IntentView(
            request=intent.request,
            category=intent.category.value,
            goal=intent.goal.value,
            confidence_percent=f"{intent.confidence:.0%}",
            entities=entities,
            requires_confirmation=(
                "sim" if intent.requires_confirmation else "não"
            ),
        )
