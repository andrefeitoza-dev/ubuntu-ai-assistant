from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_script(name: str):
    path = ROOT / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_control_uses_bundled_python_and_declares_native_dependencies() -> None:
    build_deb = load_script("build_deb")

    control = build_deb.control_text("2.0.1", "amd64")

    assert "Package: ubuntu-ai-assistant" in control
    assert "Version: 2.0.1" in control
    assert "Architecture: amd64" in control
    assert "libc6 (>= 2.35)" in control
    assert "libx11-6" in control
    assert "python3-tk" not in control


def test_wrappers_use_fixed_installation_root_without_shell_input() -> None:
    build_deb = load_script("build_deb")

    interpreter = "/opt/ubuntu-ai-assistant/runtime/cpython-3.12/bin/python3.12"
    script = build_deb.wrapper("ubuntu_ai.gui.app", "main", interpreter)

    assert 'PYTHONPATH="/opt/ubuntu-ai-assistant/lib' in script
    assert "from ubuntu_ai.gui.app import main; main()" in script
    assert interpreter in script
    assert "/usr/bin/python3" not in script
    assert '"$@"' in script


def test_desktop_entry_is_visible_and_uses_packaged_command() -> None:
    build_deb = load_script("build_deb")

    desktop = build_deb.desktop_text()

    assert "Exec=/usr/bin/ubuntu-ai-gui" in desktop
    assert "Icon=ubuntu-ai-assistant" in desktop
    assert "Terminal=false" in desktop


def test_debian_validator_requires_user_commands_and_desktop_assets() -> None:
    validate_deb = load_script("validate_deb")

    assert "./usr/bin/ubuntu-ai" in validate_deb.REQUIRED_PATHS
    assert "./usr/bin/ubuntu-ai-setup" in validate_deb.REQUIRED_PATHS
    assert "./usr/share/applications/ubuntu-ai-assistant.desktop" in (validate_deb.REQUIRED_PATHS)
