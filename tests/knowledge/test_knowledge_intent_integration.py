from tests.knowledge.fakes import FakeKnowledgeRepository
from ubuntu_ai.intent import (
    Intent,
    IntentCategory,
    IntentEntity,
    IntentGoal,
)
from ubuntu_ai.knowledge.service import KnowledgeService


def test_knowledge_search_accepts_intent() -> None:
    repository = FakeKnowledgeRepository()
    service = KnowledgeService(repository)
    intent = Intent(
        request="Instale Docker",
        category=IntentCategory.INSTALLATION,
        goal=IntentGoal.PROVISION,
        confidence=0.9,
        entities=(IntentEntity("docker"),),
    )

    assert service.search_for_intent(intent) == []
