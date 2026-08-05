from pathlib import Path

import pytest

from ubuntu_ai.config.loader import ConfigLoader, ConfigLoadError
from ubuntu_ai.config.models import PathConfig


def create_paths(tmp_path: Path) -> PathConfig:
    config_directory = tmp_path / "config"

    return PathConfig(
        config_directory=config_directory,
        data_directory=tmp_path / "data",
        cache_directory=tmp_path / "cache",
        state_directory=tmp_path / "state",
        config_file=config_directory / "config.toml",
    )


def test_loader_reads_complete_configuration(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        """
[ai]
provider = "ollama"
model = "qwen-custom:3b"
base_url = "http://127.0.0.1:11434"
timeout = 450
max_tokens = 512
temperature = 0.2
keep_alive = "15m"

[memory]
enabled = false

[knowledge]
enabled = true

[learning]
enabled = false

[reflection]
enabled = true

[logging]
level = "DEBUG"
directory = "/tmp/ubuntu-ai-logs"
max_file_size_mb = 20
backup_count = 3

[ui]
language = "pt_PT"
theme = "dark"
clear_between_tasks = true
""".strip(),
        encoding="utf-8",
    )

    settings = ConfigLoader().load_file(
        config_file,
        default_paths=create_paths(tmp_path),
    )

    assert settings.ai.model == "qwen-custom:3b"
    assert settings.ai.timeout == 450
    assert settings.ai.max_tokens == 512
    assert settings.ai.temperature == 0.2
    assert settings.memory.enabled is False
    assert settings.knowledge.enabled is True
    assert settings.learning.enabled is False
    assert settings.logging.level == "DEBUG"
    assert settings.logging.directory == Path("/tmp/ubuntu-ai-logs")
    assert settings.ui.language == "pt_PT"
    assert settings.ui.theme == "dark"
    assert settings.ui.clear_between_tasks is True


def test_loader_uses_defaults_for_missing_sections(
    tmp_path: Path,
) -> None:
    settings = ConfigLoader().load_mapping(
        {},
        default_paths=create_paths(tmp_path),
    )

    assert settings.ai.provider == "ollama"
    assert settings.ai.model == "qwen2.5:3b"
    assert settings.memory.enabled is True
    assert settings.logging.level == "INFO"
    assert settings.paths is not None


def test_loader_rejects_invalid_toml(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "config.toml"
    config_file.write_text(
        "[ai\nmodel = 'broken'",
        encoding="utf-8",
    )

    with pytest.raises(
        ConfigLoadError,
        match="Não foi possível carregar",
    ):
        ConfigLoader().load_file(
            config_file,
            default_paths=create_paths(tmp_path),
        )


def test_loader_rejects_invalid_value_type(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ConfigLoadError,
        match="valores inválidos",
    ):
        ConfigLoader().load_mapping(
            {
                "ai": {
                    "timeout": "trezentos",
                }
            },
            default_paths=create_paths(tmp_path),
        )


def test_loader_rejects_non_table_section(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ConfigLoadError,
        match="deve ser uma tabela TOML",
    ):
        ConfigLoader().load_mapping(
            {
                "ai": "ollama",
            },
            default_paths=create_paths(tmp_path),
        )