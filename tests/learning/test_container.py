from ubuntu_ai.container import Container
from ubuntu_ai.learning.engine import LearningEngine
from ubuntu_ai.learning.service import LearningService


def test_container_creates_learning_components() -> None:
    container = Container()

    assert isinstance(container.learning_service(), LearningService)
    assert isinstance(container.learning_engine(), LearningEngine)
    assert container.learning_service() is container.learning_service()
