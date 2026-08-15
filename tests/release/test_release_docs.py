from pathlib import Path


def test_release_documents_exist():
    assert Path("docs/release/CHECKLIST-v1.0.md").exists()
    assert Path("docs/release/DEMO.md").exists()
    assert Path("docs/release/KNOWN_LIMITATIONS.md").exists()
