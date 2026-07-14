from ubuntu_ai.container import Container
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.planner.planner import Planner


def test_container_creates_planner() -> None:
    container = Container()

    planner = container.planner()

    assert isinstance(planner, Planner)


def test_container_creates_pipeline() -> None:
    container = Container()

    pipeline = container.execution_pipeline()

    assert isinstance(pipeline, ExecutionPipeline)