from typing import Any

import pytest

from ubuntu_ai.tools.base import Tool
from ubuntu_ai.tools.registry import ToolRegistry


class FakeTool(Tool):
    name = "fake"
    description = "Ferramenta usada apenas em testes."

    def execute(self, **kwargs: Any) -> str:
        return "executado"


def test_register_and_get_tool() -> None:
    registry = ToolRegistry()
    tool = FakeTool()

    registry.register(tool)

    assert registry.get("fake") is tool


def test_list_names_returns_registered_tools() -> None:
    registry = ToolRegistry()
    registry.register(FakeTool())

    assert registry.list_names() == ["fake"]


def test_register_duplicate_tool_raises_error() -> None:
    registry = ToolRegistry()
    registry.register(FakeTool())

    with pytest.raises(ValueError, match="Ferramenta já registrada"):
        registry.register(FakeTool())


def test_get_unknown_tool_raises_error() -> None:
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="Ferramenta não encontrada"):
        registry.get("missing")
