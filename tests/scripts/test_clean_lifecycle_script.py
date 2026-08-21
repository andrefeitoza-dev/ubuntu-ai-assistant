from pathlib import Path


def test_clean_lifecycle_script_uses_isolated_uv_tool_without_shell() -> None:
    source = (
        Path(__file__).resolve().parents[2] / "scripts/validate_clean_lifecycle.py"
    ).read_text(encoding="utf-8")

    assert '"UV_TOOL_DIR"' in source
    assert '"UV_TOOL_BIN_DIR"' in source
    assert '"XDG_CONFIG_HOME"' in source
    assert '"tool", "install"' in source
    assert '"tool", "uninstall"' in source
    assert 'bin_dir / "ubuntu-ai"' in source
    assert 'bin_dir / "ubuntu-ai-gui"' in source
    assert 'bin_dir / "ubuntu-ai-install-launcher"' in source
    assert "os.access(path, os.X_OK)" in source
    assert "shell=False" in source
    assert "shell=True" not in source
