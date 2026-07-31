from ubuntu_ai.container.container import Container
from ubuntu_ai.semantic import SQLiteSemanticRepository


def test_container_builds_semantic_components_as_singletons() -> None:
    container = Container()

    assert isinstance(container.semantic_repository(), SQLiteSemanticRepository)
    assert container.semantic_knowledge_service() is container.semantic_knowledge_service()
    assert container.rag_context_builder() is container.rag_context_builder()
