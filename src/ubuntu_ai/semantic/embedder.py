from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Sequence

_TOKEN_PATTERN = re.compile(r"[\wÀ-ÿ]+", re.UNICODE)


class LocalHashEmbedder:
    """Gera embeddings locais determinísticos sem dependências externas.

    O algoritmo usa hashing assinado de unigramas e bigramas. Ele não substitui
    um modelo neural, mas fornece recuperação semântica leve, offline e estável
    para notebooks com pouca memória.
    """

    def __init__(self, *, dimensions: int = 256) -> None:
        if dimensions < 32:
            raise ValueError("O embedding deve possuir pelo menos 32 dimensões.")
        self._dimensions = dimensions

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed(self, text: str) -> tuple[float, ...]:
        tokens = self._tokens(text)
        vector = [0.0] * self._dimensions
        features = tokens + [f"{left}_{right}" for left, right in zip(tokens, tokens[1:])]

        for feature in features:
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            value = int.from_bytes(digest, "big")
            index = value % self._dimensions
            sign = -1.0 if value & 1 else 1.0
            vector[index] += sign

        norm = math.sqrt(sum(component * component for component in vector))
        if norm == 0:
            return tuple(vector)
        return tuple(component / norm for component in vector)

    @staticmethod
    def cosine_similarity(
        left: Sequence[float],
        right: Sequence[float],
    ) -> float:
        if len(left) != len(right):
            raise ValueError("Os vetores devem possuir a mesma dimensão.")
        similarity = sum(a * b for a, b in zip(left, right))
        return max(0.0, min(1.0, similarity))

    @staticmethod
    def _tokens(text: str) -> list[str]:
        return [token.casefold() for token in _TOKEN_PATTERN.findall(text)]
