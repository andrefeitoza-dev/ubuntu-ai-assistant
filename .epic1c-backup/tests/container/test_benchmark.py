from ubuntu_ai.container.container import Container


def test_container_reuses_benchmark_singletons() -> None:
    container = Container()

    assert container.benchmark_recorder() is container.benchmark_recorder()
    assert container.benchmark_service() is container.benchmark_service()


def test_pipeline_records_intent_planner_and_pipeline() -> None:
    container = Container()
    service = container.benchmark_service()

    container.execution_pipeline().run("Instale Docker")

    assert {record.operation for record in service.report().records} == {
        "intent",
        "planner",
        "pipeline",
    }