from ubuntu_ai.fastpath.matcher import FastMatcher


class FastPathPlanner:
    """Constrói um plano sem utilizar LLM."""

    @staticmethod
    def build(prompt: str):

        command = FastMatcher.match(prompt)

        if command is None:
            return None

        return {
            "goal": command.goal,
            "risk": command.risk,
            "estimated_seconds": command.estimated_seconds,
            "steps": [
                {
                    "title": command.goal,
                    "description": command.description,
                    "command": command.command,
                }
            ],
        }