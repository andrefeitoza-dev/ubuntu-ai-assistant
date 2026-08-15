from __future__ import annotations

from dataclasses import dataclass

from ubuntu_ai.domain.risk import RiskLevel


@dataclass(frozen=True, slots=True)
class BuiltinCommand:
    """Representa um plano determinístico simples do sistema."""

    goal: str
    title: str
    description: str
    command: tuple[str, ...]
    keywords: tuple[str, ...]
    risk: RiskLevel = RiskLevel.LOW
    estimated_seconds: int = 1


BUILTIN_COMMANDS: tuple[BuiltinCommand, ...] = (
    BuiltinCommand(
        goal="Mostrar diretório atual",
        title="Mostrar diretório atual",
        description="Exibe o diretório de trabalho atual.",
        command=("pwd",),
        keywords=(
            "diretório atual",
            "diretorio atual",
            "meu diretório",
            "meu diretorio",
            "onde estou",
            "pwd",
        ),
    ),
    BuiltinCommand(
        goal="Mostrar uso de disco",
        title="Verificar uso de disco",
        description="Exibe o uso dos sistemas de arquivos em formato legível.",
        command=("df", "-h"),
        keywords=(
            "uso de disco",
            "espaço em disco",
            "espaco em disco",
            "espaço livre",
            "espaco livre",
            "disk usage",
            "df -h",
        ),
    ),
    BuiltinCommand(
        goal="Mostrar uso de memória",
        title="Verificar memória",
        description="Exibe memória total, utilizada e disponível.",
        command=("free", "-h"),
        keywords=(
            "memória",
            "memoria",
            "memória ram",
            "memoria ram",
            "uso de memória",
            "uso de memoria",
            "ram",
            "memory",
            "free -h",
        ),
    ),
    BuiltinCommand(
        goal="Listar arquivos",
        title="Listar arquivos",
        description="Lista os arquivos do diretório atual.",
        command=("ls",),
        keywords=(
            "liste os arquivos",
            "listar arquivos",
            "mostre os arquivos",
            "mostrar arquivos",
            "arquivos desta pasta",
        ),
    ),
)
