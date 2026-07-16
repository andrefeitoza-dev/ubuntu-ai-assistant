from ubuntu_ai.ai.ollama_provider import OllamaProvider
from ubuntu_ai.container import Container
from ubuntu_ai.core.config import AppConfig
from ubuntu_ai.pipeline.execution_pipeline import ExecutionPipeline
from ubuntu_ai.planner.planner import Planner
from ubuntu_ai.services.ollama import OllamaService


def test_container_creates_planner() -> None:
    container = Container()

    planner = container.planner()

    assert isinstance(planner, Planner)


def test_container_creates_pipeline() -> None:
    container = Container()

    pipeline = container.execution_pipeline()

    assert isinstance(pipeline, ExecutionPipeline)


def test_singleton_cache_starts_empty() -> None:
    container = Container()

    assert container._singletons == {}


def test_config_is_singleton() -> None:
    container = Container()

    first = container.config()
    second = container.config()

    assert isinstance(first, AppConfig)
    assert first is second


def test_ollama_service_is_singleton() -> None:
    container = Container()

    first = container.ollama_service()
    second = container.ollama_service()

    assert isinstance(first, OllamaService)
    assert first is second


def test_ollama_service_uses_application_config() -> None:
    container = Container()

    config = container.config()
    service = container.ollama_service()

    assert service.base_url == config.ollama_base_url
    assert service.timeout == config.request_timeout


def test_ollama_provider_is_singleton() -> None:
    container = Container()

    first = container.ollama_provider()
    second = container.ollama_provider()

    assert isinstance(first, OllamaProvider)
    assert first is second


def test_ai_provider_returns_configured_provider() -> None:
    container = Container()

    provider = container.ai_provider()

    assert provider is container.ollama_provider()


def test_planner_is_transient() -> None:
    container = Container()

    first = container.planner()
    second = container.planner()

    assert first is not second


def test_execution_pipeline_is_transient() -> None:
    container = Container()

    first = container.execution_pipeline()
    second = container.execution_pipeline()

    assert first is not second