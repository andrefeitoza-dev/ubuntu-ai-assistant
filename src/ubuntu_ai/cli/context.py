from dataclasses import dataclass


@dataclass(slots=True)
class CLIContext:
    """Opções globais compartilhadas pelos comandos da CLI."""

    debug: bool = False
