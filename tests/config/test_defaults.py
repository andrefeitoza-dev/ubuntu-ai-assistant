from pathlib import Path

from ubuntu_ai.config.defaults import (
    create_default_settings,
    default_cache_directory,
    default_config_directory,
    default_config_file,
    default_data_directory,
    default_state_directory,
)


def test_default_directories_follow_xdg_environment(
    monkeypatch,
    tmp_path: Path,
) -> None:
    config_home = tmp_path / "config"
    data_home = tmp_path / "data"
    cache_home = tmp_path / "cache"
    state_home = tmp_path / "state"

    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))
    monkeypatch.setenv("XDG_DATA_HOME", str(data_home))
    monkeypatch.setenv("XDG_CACHE_HOME", str(cache_home))
    monkeypatch.setenv("XDG_STATE_HOME", str(state_home))

    assert default_config_directory() == config_home / "ubuntu-ai"
    assert default_data_directory() == data_home / "ubuntu-ai"
    assert default_cache_directory() == cache_home / "ubuntu-ai"
    assert default_state_directory() == state_home / "ubuntu-ai"
    assert default_config_file() == (
        config_home / "ubuntu-ai" / "config.toml"
    )


def test_create_default_settings_returns_complete_configuration() -> None:
    settings = create_default_settings()

    assert settings.ai.provider == "ollama"
    assert settings.ai.model == "qwen2.5:3b"
    assert settings.memory.enabled is True
    assert settings.knowledge.enabled is True
    assert settings.learning.enabled is True
    assert settings.reflection.enabled is True
    assert settings.logging.level == "INFO"
    assert settings.ui.language == "pt_BR"
    assert settings.paths is not None