from pathlib import Path

import pytest

from ubuntu_ai.config.models import (
    AIConfig,
    AppSettings,
    LoggingConfig,
    PathConfig,
)


def test_ai_config_has_safe_defaults() -> None:
    config = AIConfig()

    assert config.provider == "ollama"
    assert config.model == "qwen2.5:3b"
    assert config.timeout == 300
    assert config.max_tokens == 384
    assert config.temperature == 0.1


def test_ai_config_rejects_invalid_timeout() -> None:
    with pytest.raises(
        ValueError,
        match="timeout da IA deve ser maior que zero",
    ):
        AIConfig(timeout=0)


def test_ai_config_rejects_invalid_temperature() -> None:
    with pytest.raises(
        ValueError,
        match="temperatura deve estar entre",
    ):
        AIConfig(temperature=2.5)


def test_logging_config_rejects_invalid_level() -> None:
    with pytest.raises(
        ValueError,
        match="nível de log",
    ):
        LoggingConfig(level="INVALID")


def test_path_config_expands_user_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))

    paths = PathConfig(
        config_directory=Path("~/.config/ubuntu-ai"),
        data_directory=Path("~/.local/share/ubuntu-ai"),
        cache_directory=Path("~/.cache/ubuntu-ai"),
        state_directory=Path("~/.local/state/ubuntu-ai"),
        config_file=Path("~/.config/ubuntu-ai/config.toml"),
    )

    expanded = paths.expanded()

    assert expanded.config_directory == (tmp_path / ".config" / "ubuntu-ai")
    assert expanded.config_file == (tmp_path / ".config" / "ubuntu-ai" / "config.toml")


def test_app_settings_can_receive_paths() -> None:
    paths = PathConfig(
        config_directory=Path("/tmp/config"),
        data_directory=Path("/tmp/data"),
        cache_directory=Path("/tmp/cache"),
        state_directory=Path("/tmp/state"),
        config_file=Path("/tmp/config/config.toml"),
    )

    settings = AppSettings().with_paths(paths)

    assert settings.paths == paths
