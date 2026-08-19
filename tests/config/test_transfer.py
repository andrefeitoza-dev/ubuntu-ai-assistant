from __future__ import annotations

from pathlib import Path

import pytest

from ubuntu_ai.config import (
    ConfigRepository,
    ConfigTransferError,
    ConfigTransferService,
)


def service(tmp_path: Path) -> ConfigTransferService:
    return ConfigTransferService(ConfigRepository(tmp_path / "active.toml"))


def test_export_is_portable_private_and_excludes_paths(tmp_path: Path) -> None:
    destination = tmp_path / "export.toml"

    service(tmp_path).export_file(destination)
    content = destination.read_text(encoding="utf-8")

    assert "[ai]" in content
    assert "[paths]" not in content
    assert "directory =" not in content
    assert destination.stat().st_mode & 0o777 == 0o600


def test_import_preserves_local_paths(tmp_path: Path) -> None:
    repository = ConfigRepository(tmp_path / "local" / "config.toml")
    transfer = ConfigTransferService(repository)
    source = tmp_path / "portable.toml"
    source.write_text('[ai]\nmodel = "portable-model"\n', encoding="utf-8")

    imported = transfer.import_file(source)

    assert imported.ai.model == "portable-model"
    assert imported.paths is not None
    assert imported.paths.config_file == tmp_path / "local" / "config.toml"


@pytest.mark.parametrize("key", ("token", "api_key", "password", "private_key"))
def test_import_rejects_potential_secret_fields(tmp_path: Path, key: str) -> None:
    source = tmp_path / "unsafe.toml"
    source.write_text(f'[provider]\n{key} = "secret"\n', encoding="utf-8")

    with pytest.raises(ConfigTransferError, match="secreto"):
        service(tmp_path).import_file(source)


def test_import_rejects_symbolic_link(tmp_path: Path) -> None:
    source = tmp_path / "source.toml"
    source.write_text("[ai]\n", encoding="utf-8")
    link = tmp_path / "link.toml"
    link.symlink_to(source)

    with pytest.raises(ConfigTransferError, match="arquivo regular"):
        service(tmp_path).import_file(link)


def test_transfer_rejects_credentials_embedded_in_provider_url(tmp_path: Path) -> None:
    source = tmp_path / "unsafe-url.toml"
    source.write_text(
        '[ai]\nbase_url = "http://user:password@localhost:11434"\n',
        encoding="utf-8",
    )

    with pytest.raises(ConfigTransferError, match="credenciais"):
        service(tmp_path).import_file(source)
