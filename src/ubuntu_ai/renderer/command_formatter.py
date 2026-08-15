import shlex
from collections.abc import Sequence


class CommandFormatter:
    """Formata comandos para apresentação segura ao usuário."""

    def format(self, command: str | Sequence[str]) -> str:
        """Converte um comando em uma representação legível."""

        if isinstance(command, str):
            return command

        return shlex.join(command)
