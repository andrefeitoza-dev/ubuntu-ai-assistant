from collections.abc import Callable

from ubuntu_ai.ai.provider import AIProvider

ProviderFactory = Callable[[], AIProvider]


class AIProviderRegistry:
    """Registra fábricas de provedores de IA por identificador."""

    def __init__(self) -> None:
        self._factories: dict[str, ProviderFactory] = {}

    def register(
        self,
        name: str,
        factory: ProviderFactory,
        *,
        replace: bool = False,
    ) -> None:
        """Registra uma fábrica de provedor.

        O nome é normalizado para minúsculas. Substituições precisam ser
        explícitas para evitar alterações silenciosas na composição da
        aplicação.
        """

        normalized_name = self._normalize_name(name)

        if normalized_name in self._factories and not replace:
            raise ValueError(f"Provedor de IA já registrado: {normalized_name}")

        self._factories[normalized_name] = factory

    def create(self, name: str) -> AIProvider:
        """Cria o provedor associado ao identificador informado."""

        normalized_name = self._normalize_name(name)

        try:
            factory = self._factories[normalized_name]
        except KeyError as error:
            available = ", ".join(self.list_names()) or "nenhum"
            raise KeyError(
                f"Provedor de IA não encontrado: {normalized_name}. Disponíveis: {available}."
            ) from error

        return factory()

    def list_names(self) -> tuple[str, ...]:
        """Retorna os identificadores registrados em ordem estável."""

        return tuple(sorted(self._factories))

    def contains(self, name: str) -> bool:
        """Informa se um identificador está registrado."""

        return self._normalize_name(name) in self._factories

    @staticmethod
    def _normalize_name(name: str) -> str:
        normalized_name = name.strip().lower()
        if not normalized_name:
            raise ValueError("O nome do provedor de IA não pode estar vazio.")
        return normalized_name
