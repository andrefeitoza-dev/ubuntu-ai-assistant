from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.reflection.failure import FailureAnalysis, FailureKind


@dataclass(frozen=True, slots=True)
class RootCause:
    """Hipótese explicável sobre a causa raiz."""

    title: str
    explanation: str
    confidence: float


class RootCauseAnalyzer:
    """Produz uma hipótese de causa raiz a partir da falha classificada."""

    _CAUSES = {
        FailureKind.PERMISSION: (
            "Privilégios insuficientes",
            "O processo provavelmente não possui permissões para a operação solicitada.",
        ),
        FailureKind.NOT_FOUND: (
            "Recurso ausente",
            "O comando, arquivo ou recurso necessário não foi encontrado no ambiente.",
        ),
        FailureKind.NETWORK: (
            "Indisponibilidade de rede",
            "A operação depende de conectividade ou resolução de nomes indisponível.",
        ),
        FailureKind.DEPENDENCY: (
            "Dependência ausente ou incompatível",
            "Uma biblioteca, módulo ou pacote exigido não está disponível corretamente.",
        ),
        FailureKind.TIMEOUT: (
            "Operação excedeu o tempo limite",
            "A operação não concluiu dentro da janela esperada.",
        ),
        FailureKind.INVALID_INPUT: (
            "Entrada ou argumentos inválidos",
            "O comando recebeu argumentos incompatíveis com sua interface.",
        ),
        FailureKind.UNKNOWN: (
            "Causa não determinada",
            "Os sinais disponíveis não são suficientes para apontar uma causa raiz confiável.",
        ),
        FailureKind.NONE: (
            "Sem falha",
            "Não há falha a analisar.",
        ),
    }

    def analyze(self, failure: FailureAnalysis) -> RootCause:
        title, explanation = self._CAUSES[failure.kind]
        return RootCause(
            title=title,
            explanation=explanation,
            confidence=failure.confidence,
        )
