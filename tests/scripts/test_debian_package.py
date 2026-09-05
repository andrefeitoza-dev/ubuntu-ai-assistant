from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

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
    assert "libportaudio2" in control
    assert "speech-dispatcher" in control
    assert "python3-tk" not in control


def test_wrappers_use_fixed_installation_root_without_shell_input() -> None:
    build_deb = load_script("build_deb")

    interpreter = "/opt/ubuntu-ai-assistant/runtime/cpython-3.12/bin/python3.12"
    script = build_deb.wrapper("ubuntu-ai-gui", interpreter)

    assert 'PYTHONPATH="/opt/ubuntu-ai-assistant/lib' in script
    assert '"/opt/ubuntu-ai-assistant/lib/bin/ubuntu-ai-gui"' in script
    assert interpreter in script
    assert "/usr/bin/python3" not in script
    assert " -c " not in script
    assert '"$@"' in script


def test_entrypoint_shebangs_are_rewritten_to_final_runtime(tmp_path: Path) -> None:
    build_deb = load_script("build_deb")
    entrypoints = tmp_path / "bin"
    entrypoints.mkdir()
    command = entrypoints / "ubuntu-ai"
    command.write_text("#!/tmp/build/python3.12\nprint('ok')\n", encoding="utf-8")

    interpreter = "/opt/ubuntu-ai-assistant/runtime/cpython-3.12/bin/python3.12"
    build_deb.rewrite_entrypoint_shebangs(entrypoints, interpreter)

    assert command.read_text(encoding="utf-8").startswith(f"#!{interpreter}\n")


def test_desktop_entry_is_visible_and_uses_packaged_command() -> None:
    build_deb = load_script("build_deb")

    desktop = build_deb.desktop_text()

    assert "Exec=/usr/bin/ubuntu-ai-gui" in desktop
    assert "Icon=ubuntu-ai-assistant" in desktop
    assert "Terminal=false" in desktop


def test_setup_desktop_entry_exposes_graphical_ollama_assistant() -> None:
    build_deb = load_script("build_deb")

    desktop = build_deb.setup_desktop_text()

    assert "Name=Configurar Ubuntu AI Assistant" in desktop
    assert "Exec=/usr/bin/ubuntu-ai-setup-gui" in desktop
    assert "Terminal=false" in desktop


def test_debian_validator_requires_user_commands_and_desktop_assets() -> None:
    validate_deb = load_script("validate_deb")

    assert "./usr/bin/ubuntu-ai" in validate_deb.REQUIRED_PATHS
    assert "./usr/bin/ubuntu-ai-setup" in validate_deb.REQUIRED_PATHS
    assert "./usr/bin/ubuntu-ai-setup-gui" in validate_deb.REQUIRED_PATHS
    assert "./usr/share/applications/ubuntu-ai-assistant.desktop" in (validate_deb.REQUIRED_PATHS)


def test_debian_validator_rejects_temporary_entrypoint_shebang(tmp_path: Path) -> None:
    validate_deb = load_script("validate_deb")
    for command in validate_deb.PUBLIC_COMMANDS:
        public = tmp_path / "usr" / "bin" / command
        public.parent.mkdir(parents=True, exist_ok=True)
        public.write_text(
            "#!/bin/sh\n"
            f'exec /opt/runtime/python /opt/ubuntu-ai-assistant/lib/bin/{command} "$@"\n',
            encoding="utf-8",
        )
        internal = tmp_path / "opt" / "ubuntu-ai-assistant" / "lib" / "bin" / command
        internal.parent.mkdir(parents=True, exist_ok=True)
        internal.write_text(
            "#!/tmp/ubuntu-ai-deb-build/package/runtime/python3.12\n",
            encoding="utf-8",
        )

    with pytest.raises(ValueError, match="caminho temporário"):
        validate_deb.validate_launcher_tree(tmp_path)


def test_preinstall_cleans_only_the_package_root_during_upgrade() -> None:
    build_deb = load_script("build_deb")

    script = build_deb.pre_install_text()

    assert '"${1:-}" = "upgrade"' in script
    assert '[ -d "/opt/ubuntu-ai-assistant" ]' in script
    assert 'rm -rf -- "/opt/ubuntu-ai-assistant"' in script
    assert "$HOME" not in script
    assert ".config" not in script


def test_validator_accepts_restricted_upgrade_cleanup(tmp_path: Path) -> None:
    build_deb = load_script("build_deb")
    validate_deb = load_script("validate_deb")

    preinst = tmp_path / "preinst"
    preinst.write_text(build_deb.pre_install_text(), encoding="utf-8")

    validate_deb.validate_preinstall_tree(tmp_path)


def test_validator_rejects_cleanup_of_user_data(tmp_path: Path) -> None:
    build_deb = load_script("build_deb")
    validate_deb = load_script("validate_deb")

    preinst = tmp_path / "preinst"
    source = build_deb.pre_install_text() + '\nrm -rf "$HOME/.config"\n'
    preinst.write_text(source, encoding="utf-8")

    with pytest.raises(ValueError, match="dados do usuário"):
        validate_deb.validate_preinstall_tree(tmp_path)
