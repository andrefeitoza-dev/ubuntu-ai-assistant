from pathlib import Path

def test_core_docs_exist():
    assert Path("docs/user-guide.md").exists()
    assert Path("docs/developer-guide.md").exists()
    assert Path("docs/architecture/runtime-flow.md").exists()
