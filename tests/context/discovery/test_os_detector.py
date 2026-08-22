from pathlib import Path

from ubuntu_ai.context.discovery import OperatingSystemDetector


def test_os_release_pretty_name_is_parsed(tmp_path: Path) -> None:
    release = tmp_path / "os-release"
    release.write_text(
        'NAME="Ubuntu"\nPRETTY_NAME="Ubuntu 24.04.3 LTS"\n',
        encoding="utf-8",
    )

    values = OperatingSystemDetector._read_os_release(release)

    assert values["PRETTY_NAME"] == "Ubuntu 24.04.3 LTS"
