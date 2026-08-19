from __future__ import annotations

from pathlib import Path

import pytest

from ubuntu_ai.plugins import (
    PluginCatalog,
    PluginCatalogStatus,
    PluginLoader,
    PluginTrustError,
    PluginTrustStore,
)


def write_plugin(root: Path, *, api_version: int = 1) -> Path:
    directory = root / "demo"
    directory.mkdir()
    manifest = directory / "plugin.toml"
    manifest.write_text(
        '[plugin]\nname="demo"\nversion="1.0.0"\n'
        f'api_version={api_version}\nentrypoint="plugin:DemoPlugin"\n',
        encoding="utf-8",
    )
    (directory / "plugin.py").write_text(
        "from ubuntu_ai.plugins import UbuntuAIPlugin\n"
        "class DemoPlugin(UbuntuAIPlugin):\n"
        "    def skills(self): return ()\n",
        encoding="utf-8",
    )
    return manifest


def test_catalog_does_not_import_untrusted_plugin(tmp_path: Path) -> None:
    manifest = write_plugin(tmp_path)
    marker = manifest.parent / "imported"
    (manifest.parent / "plugin.py").write_text(
        f"from pathlib import Path\nPath({str(marker)!r}).write_text('yes')\n"
        "from ubuntu_ai.plugins import UbuntuAIPlugin\n"
        "class DemoPlugin(UbuntuAIPlugin):\n"
        "    def skills(self): return ()\n",
        encoding="utf-8",
    )
    catalog = PluginCatalog(PluginTrustStore(tmp_path / "trust.json"))

    entry = catalog.scan(tmp_path)[0]

    assert entry.status is PluginCatalogStatus.UNTRUSTED
    assert not marker.exists()


def test_default_loader_blocks_untrusted_plugin(tmp_path: Path, monkeypatch) -> None:
    manifest = write_plugin(tmp_path)
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))

    with pytest.raises(PluginTrustError):
        PluginLoader().load(manifest)


def test_approved_plugin_becomes_ready_and_store_is_private(tmp_path: Path) -> None:
    manifest = write_plugin(tmp_path)
    trust_path = tmp_path / "state" / "trust.json"
    trust = PluginTrustStore(trust_path)
    trust.approve(manifest)

    entry = PluginCatalog(trust).inspect(manifest)

    assert entry.status is PluginCatalogStatus.READY
    assert trust_path.stat().st_mode & 0o777 == 0o600


def test_change_after_approval_revokes_trust(tmp_path: Path) -> None:
    manifest = write_plugin(tmp_path)
    trust = PluginTrustStore(tmp_path / "trust.json")
    trust.approve(manifest)
    (manifest.parent / "plugin.py").write_text("# changed\n", encoding="utf-8")

    assert not trust.is_trusted(manifest)
    with pytest.raises(PluginTrustError):
        PluginLoader(trust_store=trust, require_trust=True).load(manifest)


def test_incompatible_plugin_is_reported_without_loading(tmp_path: Path) -> None:
    manifest = write_plugin(tmp_path, api_version=999)

    entry = PluginCatalog(PluginTrustStore(tmp_path / "trust.json")).inspect(manifest)

    assert entry.status is PluginCatalogStatus.INCOMPATIBLE
