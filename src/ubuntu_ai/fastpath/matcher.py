from ubuntu_ai.fastpath.registry import FAST_COMMANDS


class FastMatcher:
    """Localiza comandos conhecidos."""

    @staticmethod
    def match(prompt: str):

        normalized = prompt.lower()

        for command in FAST_COMMANDS:

            for keyword in command.keywords:

                if keyword in normalized:
                    return command

        return None