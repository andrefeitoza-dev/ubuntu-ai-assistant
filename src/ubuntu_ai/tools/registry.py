from ubuntu_ai.tools.base import Tool


class ToolRegistry:
    """Registra e disponibiliza ferramentas pelo nome."""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Ferramenta já registrada: {tool.name}")

        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Ferramenta não encontrada: {name}") from exc

    def list_names(self) -> list[str]:
        return sorted(self._tools)