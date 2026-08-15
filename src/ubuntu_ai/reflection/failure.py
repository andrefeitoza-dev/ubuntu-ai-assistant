from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class FailureKind(StrEnum):
    """Categorias de falha compreendidas pelo Reflection V2."""

    NONE = "none"
    PERMISSION = "permission"
    NOT_FOUND = "not_found"
    NETWORK = "network"
    DEPENDENCY = "dependency"
    TIMEOUT = "timeout"
    INVALID_INPUT = "invalid_input"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class FailureAnalysis:
    """Resultado estruturado da análise de uma falha."""

    kind: FailureKind
    confidence: float
    summary: str
    evidence: tuple[str, ...] = ()

    @property
    def failed(self) -> bool:
        return self.kind is not FailureKind.NONE


class FailureClassifier:
    """Classifica falhas usando sinais determinísticos e explicáveis."""

    _PATTERNS: tuple[tuple[FailureKind, tuple[str, ...]], ...] = (
        (
            FailureKind.PERMISSION,
            (
                "permission denied",
                "operation not permitted",
                "not permitted",
            ),
        ),
        (
            FailureKind.NOT_FOUND,
            (
                "command not found",
                "no such file or directory",
                "not found",
            ),
        ),
        (
            FailureKind.NETWORK,
            (
                "network is unreachable",
                "connection refused",
                "temporary failure in name resolution",
                "could not resolve",
                "connection timed out",
            ),
        ),
        (
            FailureKind.DEPENDENCY,
            (
                "module not found",
                "modulenotfounderror",
                "dependency",
                "package is not installed",
                "cannot import",
            ),
        ),
        (
            FailureKind.TIMEOUT,
            (
                "timed out",
                "timeout",
                "deadline exceeded",
            ),
        ),
        (
            FailureKind.INVALID_INPUT,
            (
                "invalid option",
                "invalid argument",
                "unrecognized argument",
                "usage:",
            ),
        ),
    )

    def classify(
        self,
        *,
        success: bool,
        message: str = "",
        stdout: str = "",
        stderr: str = "",
    ) -> FailureAnalysis:
        if success:
            return FailureAnalysis(
                kind=FailureKind.NONE,
                confidence=1.0,
                summary="Execução concluída sem falha detectada.",
            )

        corpus = "\n".join((message, stdout, stderr)).lower()

        for kind, patterns in self._PATTERNS:
            evidence = tuple(pattern for pattern in patterns if pattern in corpus)
            if evidence:
                confidence = min(0.98, 0.72 + 0.08 * len(evidence))
                return FailureAnalysis(
                    kind=kind,
                    confidence=round(confidence, 2),
                    summary=f"Falha classificada como {kind.value}.",
                    evidence=evidence,
                )

        return FailureAnalysis(
            kind=FailureKind.UNKNOWN,
            confidence=0.35,
            summary="Falha detectada, mas sem causa conhecida.",
        )
