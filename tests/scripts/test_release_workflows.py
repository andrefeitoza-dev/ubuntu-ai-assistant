from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ci_validates_quality_architecture_docs_and_artifacts() -> None:
    source = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    for expected in (
        "ruff check src tests scripts",
        "pytest",
        "check_architecture.py",
        "architecture_audit.py",
        "mkdocs build --strict",
        "release_artifacts.py validate",
        "validate_clean_lifecycle.py",
    ):
        assert expected in source


def test_release_requires_matching_tag_checksums_and_keyless_attestation() -> None:
    source = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")

    assert 'test "${GITHUB_REF_NAME}" = "v${PACKAGE_VERSION}"' in source
    assert "release_artifacts.py checksums" in source
    assert "release_artifacts.py verify" in source
    assert "actions/attest-build-provenance@v2" in source
    assert "id-token: write" in source
    assert "dist/SHA256SUMS" in source
    assert "PRIVATE_KEY" not in source


def test_ci_installs_tkinter_before_launcher_validation() -> None:
    workflow = (Path(__file__).parents[2] / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    dependency = workflow.index("sudo apt-get install --yes python3-tk")
    lifecycle = workflow.index("scripts/validate_clean_lifecycle.py")

    assert dependency < lifecycle
