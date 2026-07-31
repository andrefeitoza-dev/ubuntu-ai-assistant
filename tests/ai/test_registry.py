from dataclasses import dataclass

import pytest

from ubuntu_ai.ai.models import AIRequest, AIResponse
from ubuntu_ai.ai.provider import AIProvider
from ubuntu_ai.ai.registry import AIProviderRegistry


@dataclass
class StubProvider(AIProvider):
    content: str = "ok"

    def generate(self, request: AIRequest) -> AIResponse:
        return AIResponse(content=f"{self.content}:{request.prompt}")


def test_registry_creates_registered_provider() -> None:
    provider = StubProvider()
    registry = AIProviderRegistry()
    registry.register("Custom", lambda: provider)

    assert registry.create(" custom ") is provider
    assert registry.list_names() == ("custom",)


def test_registry_rejects_duplicate_without_explicit_replace() -> None:
    registry = AIProviderRegistry()
    registry.register("custom", StubProvider)

    with pytest.raises(ValueError, match="já registrado"):
        registry.register("CUSTOM", StubProvider)


def test_registry_can_replace_provider_explicitly() -> None:
    first = StubProvider("first")
    second = StubProvider("second")
    registry = AIProviderRegistry()
    registry.register("custom", lambda: first)
    registry.register("custom", lambda: second, replace=True)

    assert registry.create("custom") is second


def test_registry_reports_available_providers_for_unknown_name() -> None:
    registry = AIProviderRegistry()
    registry.register("ollama", StubProvider)

    with pytest.raises(KeyError, match="Disponíveis: ollama"):
        registry.create("missing")


def test_registry_rejects_empty_name() -> None:
    registry = AIProviderRegistry()

    with pytest.raises(ValueError, match="não pode estar vazio"):
        registry.contains("   ")
