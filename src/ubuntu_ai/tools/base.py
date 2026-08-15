from abc import ABC, abstractmethod
from typing import Any


class Tool(ABC):
    """Contrato base para todas as ferramentas do Ubuntu AI Assistant."""

    name: str
    description: str

    @abstractmethod
    def execute(self, **kwargs: Any) -> Any:
        """Executa a ferramenta."""
