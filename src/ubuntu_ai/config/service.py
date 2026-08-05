from __future__ import annotations

from ubuntu_ai.config.models import AppSettings
from ubuntu_ai.config.repository import ConfigRepository


class ConfigService:
    """Serviço responsável por fornecer acesso às configurações."""

    def __init__(
        self,
        repository: ConfigRepository | None = None,
    ) -> None:
        self._repository = repository or ConfigRepository()
        self._settings: AppSettings | None = None

    @property
    def settings(self) -> AppSettings:
        """Retorna as configurações carregadas."""

        if self._settings is None:
            self._settings = self._repository.load()

        return self._settings

    def reload(self) -> AppSettings:
        """Recarrega o arquivo de configuração."""

        self._settings = self._repository.load()
        return self._settings

    def save(
        self,
        settings: AppSettings,
    ) -> None:
        """Persiste novas configurações."""

        self._repository.save(settings)
        self._settings = settings

    def reset(self) -> AppSettings:
        """Restaura a configuração padrão."""

        self._settings = self._repository.reset()
        return self._settings

    @property
    def repository(self) -> ConfigRepository:
        return self._repository