from pathlib import Path

from ubuntu_ai.desktop import DesktopApplicationCatalog


def write_entry(
    root: Path,
    desktop_id: str,
    *,
    name: str = "GIMP",
    exec_value: str = "gimp %U",
    extra: str = "",
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    path = root / f"{desktop_id}.desktop"
    path.write_text(
        f"[Desktop Entry]\nType=Application\nName={name}\nExec={exec_value}\n{extra}",
        encoding="utf-8",
    )
    path.chmod(0o644)
    return path


def test_discovers_application_by_name_and_desktop_id(tmp_path: Path) -> None:
    write_entry(tmp_path, "org.gimp.GIMP")
    catalog = DesktopApplicationCatalog((tmp_path,))

    assert catalog.find("Gimp").desktop_id == "org.gimp.GIMP"  # type: ignore[union-attr]
    assert catalog.find("org.gimp.GIMP").name == "GIMP"  # type: ignore[union-attr]
    assert catalog.contains_id("org.gimp.GIMP")


def test_prefers_portuguese_localized_name(tmp_path: Path) -> None:
    write_entry(
        tmp_path,
        "org.example.Editor",
        name="Text Editor",
        extra="Name[pt_BR]=Editor de Texto\n",
    )

    application = DesktopApplicationCatalog((tmp_path,)).find("editor de texto")

    assert application is not None
    assert application.name == "Editor de Texto"


def test_rejects_hidden_writable_and_shell_entries(tmp_path: Path) -> None:
    write_entry(tmp_path, "hidden", extra="Hidden=true\n")
    writable = write_entry(tmp_path, "writable")
    writable.chmod(0o666)
    write_entry(tmp_path, "shell", exec_value="sh -c 'touch /tmp/unsafe'")

    catalog = DesktopApplicationCatalog((tmp_path,))

    assert catalog.applications == ()


def test_rejects_ambiguous_application_name(tmp_path: Path) -> None:
    write_entry(tmp_path, "first", name="Editor")
    write_entry(tmp_path, "second", name="Editor", exec_value="other-editor %U")

    assert DesktopApplicationCatalog((tmp_path,)).find("Editor") is None


def test_does_not_follow_entry_outside_trusted_root(tmp_path: Path) -> None:
    root = tmp_path / "applications"
    outside = write_entry(tmp_path / "outside", "outside")
    root.mkdir()
    (root / "outside.desktop").symlink_to(outside)

    assert DesktopApplicationCatalog((root,)).applications == ()
