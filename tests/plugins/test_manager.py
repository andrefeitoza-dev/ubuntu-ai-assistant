from pathlib import Path

from ubuntu_ai.plugins import PluginManager, PluginRegistry
from ubuntu_ai.skills import SkillRegistry


def _write_plugin(root: Path) -> Path:
    package = root / "demo_plugin"
    package.mkdir()
    (package / "plugin.toml").write_text(
        '[plugin]\nname="demo-plugin"\nversion="1.0.0"\napi_version=1\n'
        'entrypoint="plugin:DemoPlugin"\n',
        encoding="utf-8",
    )
    (package / "plugin.py").write_text(
        "from ubuntu_ai.plugins import UbuntuAIPlugin\n"
        "class DemoPlugin(UbuntuAIPlugin):\n"
        "    def skills(self):\n"
        "        return ()\n",
        encoding="utf-8",
    )
    return package / "plugin.toml"


def test_manager_discovers_and_installs_plugin(tmp_path: Path) -> None:
    manifest = _write_plugin(tmp_path)
    registry = PluginRegistry()
    manager = PluginManager(registry, SkillRegistry())

    assert manager.discover(tmp_path) == (manifest,)
    loaded = manager.install(manifest)

    assert loaded.manifest.name == "demo-plugin"
    assert registry.get("demo-plugin") is loaded


def test_manager_uninstalls_and_shutdowns_plugin(tmp_path: Path) -> None:
    manifest = _write_plugin(tmp_path)
    registry = PluginRegistry()
    manager = PluginManager(registry, SkillRegistry())
    manager.install(manifest)

    removed = manager.uninstall("demo-plugin")

    assert removed.manifest.name == "demo-plugin"
    assert registry.all() == ()
