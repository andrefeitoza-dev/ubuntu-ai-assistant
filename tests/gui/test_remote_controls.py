from pathlib import Path

from ubuntu_ai.gui import remote_controls


def test_remote_button_text_preserves_target_and_state() -> None:
    assert (
        remote_controls.remote_button_text(
            "local",
            expanded=False,
        )
        == "Computador: local  ▾"
    )

    assert (
        remote_controls.remote_button_text(
            "servidor-tcc",
            expanded=True,
        )
        == "Computador: servidor-tcc  ▴"
    )


def test_remote_component_only_builds_controls() -> None:
    source = Path(remote_controls.__file__).read_text(
        encoding="utf-8",
    )

    assert "tk.OptionMenu(" in source
    assert '"Diagnosticar"' in source
    assert "register_remote_host" not in source
    assert "remove_remote_host" not in source
    assert "remote_diagnostics" not in source
    assert "threading.Thread" not in source
