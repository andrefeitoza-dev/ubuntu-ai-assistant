from enum import StrEnum


class Lifetime(StrEnum):
    """Tempo de vida de uma dependência."""

    SINGLETON = "singleton"
    TRANSIENT = "transient"
