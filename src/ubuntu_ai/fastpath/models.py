from dataclasses import dataclass


@dataclass(frozen=True)
class FastCommand:
    """Representa um comando determinístico executado sem IA."""

    goal: str
    keywords: tuple[str, ...]
    command: list[str]
    description: str
    risk: str = "LOW"
    estimated_seconds: int = 1