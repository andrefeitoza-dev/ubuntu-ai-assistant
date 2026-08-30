from pathlib import Path


def test_version_file():
    assert Path("VERSION").read_text().strip() == "2.1.0"
