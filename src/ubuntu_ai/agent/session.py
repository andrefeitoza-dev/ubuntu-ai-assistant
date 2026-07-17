from ubuntu_ai.agent.models import AgentSession


class SessionManager:
    """Gerencia a sessão atual do agente."""

    def __init__(self) -> None:
        self._session = AgentSession()

    @property
    def session(self) -> AgentSession:
        """Retorna a sessão ativa."""

        return self._session

    def remember(self, message: str) -> None:
        """Armazena uma mensagem no histórico."""

        self._session.remember(message)

    def reset(self) -> None:
        """Reinicia completamente a sessão."""

        self._session.clear()