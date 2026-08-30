from __future__ import annotations

import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContextResolution:
    request: str | None = None
    message: str | None = None


class ReadOnlyConversationContext:
    """Resolve referências curtas sem reutilizar ações ou trocar de destino."""

    _REPEAT = frozenset(
        {
            "repita a consulta",
            "repita essa consulta",
            "consulte novamente",
            "mostre novamente",
            "mostre isso novamente",
        }
    )
    _AMBIGUOUS_ACTION = frozenset(
        {
            "abra o primeiro",
            "abra o segundo",
            "execute novamente",
            "faca novamente",
            "faca isso",
            "repita a acao",
        }
    )

    def __init__(self) -> None:
        self._last_request: str | None = None
        self._last_target: str | None = None

    def remember(self, request: str, *, target: str) -> None:
        normalized = request.strip()
        if normalized:
            self._last_request = normalized
            self._last_target = target.strip().casefold()

    def resolve(self, request: str, *, target: str) -> ContextResolution:
        normalized = self._normalize(request)
        if normalized in self._AMBIGUOUS_ACTION:
            return ContextResolution(
                message=(
                    "Não vou repetir ou escolher uma ação por referência ambígua. "
                    "Informe explicitamente o aplicativo, arquivo, site ou operação."
                )
            )
        if normalized not in self._REPEAT:
            return ContextResolution(request=request)
        if self._last_request is None:
            return ContextResolution(
                message="Não há uma consulta local anterior nesta sessão para repetir."
            )
        if self._last_target != target.strip().casefold():
            return ContextResolution(
                message=(
                    "O destino mudou desde a consulta anterior. Faça uma nova pergunta "
                    "explícita para evitar misturar computadores."
                )
            )
        return ContextResolution(request=self._last_request)

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFKD", value.strip().casefold())
        return normalized.encode("ascii", "ignore").decode().rstrip(".?!")
