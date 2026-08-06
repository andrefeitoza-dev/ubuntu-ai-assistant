from __future__ import annotations

from ubuntu_ai.intent.classifier import RuleBasedIntentClassifier
from ubuntu_ai.intent.models import Intent
from ubuntu_ai.intent.repository import IntentRepository


class IntentService:
    """Coordena classificação e persistência opcional de intenções."""

    def __init__(
        self,
        classifier: RuleBasedIntentClassifier | None = None,
        repository: IntentRepository | None = None,
    ) -> None:
        self._classifier = classifier or RuleBasedIntentClassifier()
        self._repository = repository

    def analyze(self, request: str) -> Intent:
        intent = self._classifier.classify(request)
        if self._repository is not None:
            self._repository.save(intent)
        return intent

    def recent(self, limit: int = 20) -> tuple[Intent, ...]:
        if self._repository is None:
            return ()
        return self._repository.list_recent(limit)
