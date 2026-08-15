from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.intent.entities import EntityExtractor
from ubuntu_ai.intent.models import Intent, IntentCategory, IntentGoal


@dataclass(frozen=True, slots=True)
class ClassificationRule:
    keywords: tuple[str, ...]
    category: IntentCategory
    goal: IntentGoal
    confidence: float
    requires_confirmation: bool = False


class RuleBasedIntentClassifier:
    """Classificador determinístico e extensível para a primeira versão do domínio."""

    DEFAULT_RULES: tuple[ClassificationRule, ...] = (
        ClassificationRule(
            keywords=("instale", "instalar", "install"),
            category=IntentCategory.INSTALLATION,
            goal=IntentGoal.PROVISION,
            confidence=0.96,
            requires_confirmation=True,
        ),
        ClassificationRule(
            keywords=("remova", "remover", "desinstale", "uninstall"),
            category=IntentCategory.MAINTENANCE,
            goal=IntentGoal.REMOVE,
            confidence=0.96,
            requires_confirmation=True,
        ),
        ClassificationRule(
            keywords=("configure", "configurar", "ajuste", "setup"),
            category=IntentCategory.CONFIGURATION,
            goal=IntentGoal.CONFIGURE,
            confidence=0.93,
            requires_confirmation=True,
        ),
        ClassificationRule(
            keywords=("atualize", "atualizar", "update", "upgrade"),
            category=IntentCategory.MAINTENANCE,
            goal=IntentGoal.UPDATE,
            confidence=0.92,
            requires_confirmation=True,
        ),
        ClassificationRule(
            keywords=("não funciona", "erro", "falha", "diagnostique", "problema"),
            category=IntentCategory.DIAGNOSIS,
            goal=IntentGoal.REPAIR,
            confidence=0.90,
        ),
        ClassificationRule(
            keywords=("mostre", "mostrar", "liste", "listar", "verifique", "status"),
            category=IntentCategory.QUERY,
            goal=IntentGoal.INSPECT,
            confidence=0.88,
        ),
        ClassificationRule(
            keywords=("crie", "desenvolva", "ambiente", "projeto"),
            category=IntentCategory.DEVELOPMENT,
            goal=IntentGoal.PROVISION,
            confidence=0.82,
            requires_confirmation=True,
        ),
    )

    def __init__(
        self,
        entity_extractor: EntityExtractor | None = None,
        rules: tuple[ClassificationRule, ...] | None = None,
    ) -> None:
        self._entity_extractor = entity_extractor or EntityExtractor()
        self._rules = rules or self.DEFAULT_RULES

    def classify(self, request: str) -> Intent:
        normalized = request.strip()
        if not normalized:
            raise ValueError("A solicitação não pode estar vazia.")

        lowered = normalized.lower()
        for rule in self._rules:
            if any(keyword in lowered for keyword in rule.keywords):
                return Intent(
                    request=normalized,
                    category=rule.category,
                    goal=rule.goal,
                    confidence=rule.confidence,
                    entities=self._entity_extractor.extract(normalized),
                    requires_confirmation=rule.requires_confirmation,
                    metadata={"classifier": "rule-based"},
                )

        return Intent(
            request=normalized,
            category=IntentCategory.UNKNOWN,
            goal=IntentGoal.UNKNOWN,
            confidence=0.30,
            entities=self._entity_extractor.extract(normalized),
            metadata={"classifier": "rule-based"},
        )
