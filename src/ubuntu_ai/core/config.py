from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppConfig:
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    request_timeout: int = 120
    command_timeout: int = 30
    language: str = "pt-BR"
    safe_mode: bool = True
    data_dir: Path = Path.home() / ".local" / "share" / "ubuntu-ai"
    log_dir: Path = Path.home() / ".local" / "state" / "ubuntu-ai" / "logs"
