from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FailureDiagnostic:
    cause: str
    next_action: str

    def render(self) -> str:
        return f"Causa provável: {self.cause} Próxima ação: {self.next_action}"


class FailureDiagnosticService:
    """Classifica falhas conhecidas sem executar recuperação automática."""

    _RULES = (
        (
            ("permission denied", "permissão negada", "operation not permitted", "errno 13"),
            "o usuário atual não possui permissão para a operação.",
            "revise o destino e as permissões; nenhuma elevação automática será tentada.",
        ),
        (
            ("no such file or directory", "arquivo ou diretório inexistente", "errno 2"),
            "o arquivo, aplicativo ou recurso solicitado não foi encontrado.",
            "confirme o nome e se o recurso está instalado ou ainda existe.",
        ),
        (
            ("timed out", "timeout", "tempo limite"),
            "a operação excedeu o tempo limite configurado.",
            "verifique a conectividade ou tente novamente com uma consulta mais específica.",
        ),
        (
            (
                "temporary failure in name resolution",
                "name or service not known",
                "network is unreachable",
            ),
            "a rede ou a resolução de nomes está indisponível.",
            "confirme a conexão e o endereço antes de repetir a operação.",
        ),
        (
            ("no space left on device", "sem espaço disponível"),
            "não há espaço livre suficiente no dispositivo.",
            "consulte o uso do disco e escolha explicitamente o que pode ser removido.",
        ),
        (
            ("command not found", "module not found", "no module named"),
            "uma dependência necessária não está disponível.",
            "confirme a instalação da dependência; nenhuma instalação automática será iniciada.",
        ),
        (
            ("invalid option", "invalid argument", "argumento inválido"),
            "a solicitação contém uma opção ou argumento incompatível.",
            "revise a prévia e informe parâmetros válidos.",
        ),
    )

    @classmethod
    def analyze(cls, detail: str) -> FailureDiagnostic:
        normalized = detail.casefold()
        for markers, cause, next_action in cls._RULES:
            if any(marker in normalized for marker in markers):
                return FailureDiagnostic(cause, next_action)
        return FailureDiagnostic(
            "os dados disponíveis não permitem identificar a falha com segurança.",
            "revise a mensagem técnica sanitizada e tente uma solicitação mais específica.",
        )
