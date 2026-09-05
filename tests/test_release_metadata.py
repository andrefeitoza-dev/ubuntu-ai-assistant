import tomllib
from pathlib import Path

from ubuntu_ai.version import FALLBACK_VERSION

ROOT = Path(__file__).resolve().parents[1]


def test_release_versions_are_consistent() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["version"] == "2.3.5"
    assert FALLBACK_VERSION == "2.3.5"
    assert (ROOT / "VERSION").read_text(encoding="utf-8").strip() == "2.3.5"


def test_release_identifies_creator_and_project_homepage() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    debian_builder = (ROOT / "scripts/build_deb.py").read_text(encoding="utf-8")

    assert pyproject["project"]["authors"] == [{"name": "Andre Anderson Feitoza"}]
    assert "Maintainer: Andre Anderson Feitoza" in debian_builder
    assert "Homepage: https://github.com/andrefeitoza-dev/ubuntu-ai-assistant" in debian_builder


def test_release_documentation_exists() -> None:
    assert (ROOT / "CHANGELOG.md").is_file()
    assert (ROOT / "LICENSE").read_text(encoding="utf-8").startswith("MIT License")
    assert (ROOT / "docs/releases/v0.6.0.md").is_file()
