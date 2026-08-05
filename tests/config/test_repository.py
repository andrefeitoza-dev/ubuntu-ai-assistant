from dataclasses import replace
from pathlib import Path

from ubuntu_ai.config.models import AIConfig
from ubuntu_ai.config.repository import ConfigRepository


def test_repository_creates_default_configuration(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "ubuntu-ai" / "config.toml"
    repository = ConfigRepository(config_file=config_file)

    settings = repository.load()

    assert config_file.is_file()
    assert settings.ai.model == "qwen2.5:3b"
    assert settings.paths is not None
    assert settings.paths.config_file == config_file


def test_repository_saves_and_loads_configuration(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "config.toml"
    repository = ConfigRepository(config_file=config_file)

    original_settings = repository.load()
    changed_settings = replace(
        original_settings,
        ai=AIConfig(
            provider="ollama",
            model="qwen-custom:3b",
            base_url="http://127.0.0.1:11434",
            timeout=450,
            max_tokens=512,
            temperature=0.2,
            keep_alive="15m",
        ),
    )

    repository.save(changed_settings)
    loaded_settings = repository.load()

    assert loaded_settings.ai.model == "qwen-custom:3b"
    assert loaded_settings.ai.timeout == 450
    assert loaded_settings.ai.max_tokens == 512
    assert loaded_settings.ai.temperature == 0.2


def test_repository_serializes_valid_toml(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "config.toml"
    repository = ConfigRepository(config_file=config_file)

    repository.load()

    content = config_file.read_text(encoding="utf-8")

    assert '[ai]' in content
    assert 'model = "qwen2.5:3b"' in content
    assert "timeout = 300" in content
    assert "[memory]" in content
    assert "enabled = true" in content
    assert "[paths]" in content


def test_repository_reset_restores_defaults(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "config.toml"
    repository = ConfigRepository(config_file=config_file)

    settings = repository.load()
    changed_settings = replace(
        settings,
        ai=replace(
            settings.ai,
            model="temporary-model",
            timeout=999,
        ),
    )

    repository.save(changed_settings)

    reset_settings = repository.reset()
    loaded_settings = repository.load()

    assert reset_settings.ai.model == "qwen2.5:3b"
    assert loaded_settings.ai.model == "qwen2.5:3b"
    assert loaded_settings.ai.timeout == 300


def test_repository_exists_reports_file_state(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "config.toml"
    repository = ConfigRepository(config_file=config_file)

    assert repository.exists() is False

    repository.load()

    assert repository.exists() is True