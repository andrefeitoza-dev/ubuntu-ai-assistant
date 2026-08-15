from pathlib import Path

import pytest

from ubuntu_ai.plugins import PluginManifest, PluginManifestError


def test_manifest_loads_toml(tmp_path: Path) -> None:
    path = tmp_path / "plugin.toml"
    path.write_text(
        '[plugin]\nname="demo"\nversion="1.0.0"\napi_version=1\n'
        'entrypoint="demo:Plugin"\npermissions=["knowledge.read"]\n',
        encoding="utf-8",
    )

    manifest = PluginManifest.load(path)

    assert manifest.name == "demo"
    assert manifest.permissions == ("knowledge.read",)


def test_manifest_rejects_entrypoint_without_object() -> None:
    with pytest.raises(PluginManifestError):
        PluginManifest.from_mapping(
            {"name": "demo", "version": "1", "api_version": 1, "entrypoint": "demo"}
        )
