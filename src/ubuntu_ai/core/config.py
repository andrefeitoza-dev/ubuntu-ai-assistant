from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class AppConfig:
    ai_provider: str = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    request_timeout: int = 300
    ollama_num_predict: int = 384
    ollama_temperature: float = 0.1
    ollama_keep_alive: str = "10m"
    command_timeout: int = 30
    language: str = "pt-BR"
    safe_mode: bool = True
    agent_loop_max_iterations: int = 5
    agent_loop_max_stalled_iterations: int = 2
    data_dir: Path = Path.home() / ".local" / "share" / "ubuntu-ai"
    log_dir: Path = Path.home() / ".local" / "state" / "ubuntu-ai" / "logs"
