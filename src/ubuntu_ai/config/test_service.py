from dataclasses import replace
from pathlib import Path

from ubuntu_ai.config.models import AIConfig
from ubuntu_ai.config.repository import ConfigRepository
from ubuntu_ai.config.service import ConfigService


def test_service_lazy_load(tmp_path: Path) -> None:
    repository = ConfigRepository(
        config_file=tmp_path / "config.toml"
    )

    service = ConfigService(repository)

    assert service.settings.ai.model == "qwen2.5:3b"


def test_service_reload(tmp_path: Path) -> None:
    repository = ConfigRepository(
        config_file=tmp_path / "config.toml"
    )

    service = ConfigService(repository)

    settings = service.settings

    changed = replace(
        settings,
        ai=replace(
            settings.ai,
            model="novo-modelo",
        ),
    )

    repository.save(changed)

    reloaded = service.reload()

    assert reloaded.ai.model == "novo-modelo"


def test_service_reset(tmp_path: Path) -> None:
    repository = ConfigRepository(
        config_file=tmp_path / "config.toml"
    )

    service = ConfigService(repository)

    modified = replace(
        service.settings,
        ai=AIConfig(
            provider="ollama",
            model="modelo-temporario",
            base_url="http://localhost:11434",
            timeout=999,
            max_tokens=100,
            temperature=0.5,
            keep_alive="5m",
        ),
    )

    service.save(modified)

    reset = service.reset()

    assert reset.ai.model == "qwen2.5:3b"
    assert reset.ai.timeout == 300


def test_service_save_updates_cache(tmp_path: Path) -> None:
    repository = ConfigRepository(
        config_file=tmp_path / "config.toml"
    )

    service = ConfigService(repository)

    updated = replace(
        service.settings,
        ai=replace(
            service.settings.ai,
            timeout=600,
        ),
    )

    service.save(updated)

    assert service.settings.ai.timeout == 600