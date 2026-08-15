from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AIConfig:
    """Configuração do provedor de inteligência artificial."""

    provider: str = "ollama"
    model: str = "qwen2.5:3b"
    base_url: str = "http://localhost:11434"
    timeout: int = 300
    max_tokens: int = 384
    temperature: float = 0.1
    keep_alive: str = "10m"

    def __post_init__(self) -> None:
        if not self.provider.strip():
            raise ValueError("O provedor de IA não pode estar vazio.")

        if not self.model.strip():
            raise ValueError("O modelo de IA não pode estar vazio.")

        if not self.base_url.strip():
            raise ValueError("A URL do provedor de IA não pode estar vazia.")

        if self.timeout <= 0:
            raise ValueError("O timeout da IA deve ser maior que zero.")

        if self.max_tokens <= 0:
            raise ValueError("O limite de tokens deve ser maior que zero.")

        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("A temperatura deve estar entre 0.0 e 2.0.")


@dataclass(frozen=True, slots=True)
class FeatureConfig:
    """Configuração de ativação de uma funcionalidade."""

    enabled: bool = True


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    """Configuração de logging da aplicação."""

    level: str = "INFO"
    directory: Path = Path("~/.local/state/ubuntu-ai/logs")
    max_file_size_mb: int = 10
    backup_count: int = 5

    def __post_init__(self) -> None:
        normalized_level = self.level.strip().upper()
        valid_levels = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        if normalized_level not in valid_levels:
            raise ValueError("O nível de log deve ser DEBUG, INFO, WARNING, ERROR ou CRITICAL.")

        if self.max_file_size_mb <= 0:
            raise ValueError("O tamanho máximo do arquivo de log deve ser maior que zero.")

        if self.backup_count < 0:
            raise ValueError("A quantidade de arquivos de backup não pode ser negativa.")


@dataclass(frozen=True, slots=True)
class UIConfig:
    """Configuração da interface do usuário."""

    language: str = "pt_BR"
    theme: str = "default"
    clear_between_tasks: bool = False

    def __post_init__(self) -> None:
        if not self.language.strip():
            raise ValueError("O idioma da interface não pode estar vazio.")

        if not self.theme.strip():
            raise ValueError("O tema da interface não pode estar vazio.")


@dataclass(frozen=True, slots=True)
class PathConfig:
    """Diretórios utilizados pela aplicação."""

    config_directory: Path
    data_directory: Path
    cache_directory: Path
    state_directory: Path
    config_file: Path

    def expanded(self) -> PathConfig:
        """Retorna os caminhos com o diretório do usuário expandido."""

        return PathConfig(
            config_directory=self.config_directory.expanduser(),
            data_directory=self.data_directory.expanduser(),
            cache_directory=self.cache_directory.expanduser(),
            state_directory=self.state_directory.expanduser(),
            config_file=self.config_file.expanduser(),
        )


@dataclass(frozen=True, slots=True)
class AppSettings:
    """Agrega toda a configuração do Ubuntu AI Assistant."""

    ai: AIConfig = field(default_factory=AIConfig)
    memory: FeatureConfig = field(default_factory=FeatureConfig)
    knowledge: FeatureConfig = field(default_factory=FeatureConfig)
    learning: FeatureConfig = field(default_factory=FeatureConfig)
    reflection: FeatureConfig = field(default_factory=FeatureConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    ui: UIConfig = field(default_factory=UIConfig)
    paths: PathConfig | None = None

    def with_paths(self, paths: PathConfig) -> AppSettings:
        """Cria uma cópia das configurações com caminhos definidos."""

        return AppSettings(
            ai=self.ai,
            memory=self.memory,
            knowledge=self.knowledge,
            learning=self.learning,
            reflection=self.reflection,
            logging=self.logging,
            ui=self.ui,
            paths=paths,
        )
