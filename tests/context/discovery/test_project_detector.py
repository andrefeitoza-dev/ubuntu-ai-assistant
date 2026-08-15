from pathlib import Path

from ubuntu_ai.context.discovery.project_detector import ProjectDetector


def test_detect_project_from_git(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()

    detector = ProjectDetector()

    assert detector.detect(str(tmp_path)) == tmp_path.name


def test_detect_project_from_pyproject(tmp_path: Path) -> None:
    (tmp_path / "pyproject.toml").touch()

    detector = ProjectDetector()

    assert detector.detect(str(tmp_path)) == tmp_path.name


def test_returns_none_when_not_project(tmp_path: Path) -> None:
    detector = ProjectDetector()

    assert detector.detect(str(tmp_path)) is None
