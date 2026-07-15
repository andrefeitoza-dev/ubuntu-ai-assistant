from pathlib import Path

from ubuntu_ai.core.config import AppConfig


def test_app_config_has_expected_defaults() -> None:
    config = AppConfig()

    assert config.ollama_base_url == "http://localhost:11434"
    assert config.ollama_model == "qwen2.5:3b"
    assert config.request_timeout == 120
    assert config.command_timeout == 30
    assert config.language == "pt-BR"
    assert config.safe_mode is True


def test_app_config_uses_user_directories() -> None:
    config = AppConfig()

    assert config.data_dir == Path.home() / ".local" / "share" / "ubuntu-ai"
    assert config.log_dir == Path.home() / ".local" / "state" / "ubuntu-ai" / "logs"