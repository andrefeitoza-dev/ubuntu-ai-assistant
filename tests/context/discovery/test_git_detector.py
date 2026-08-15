from pathlib import Path

from ubuntu_ai.context.discovery.git_detector import GitDetector


def test_detect_git_repository(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()

    detector = GitDetector()

    assert detector.is_repository(str(tmp_path))


def test_non_repository(tmp_path: Path) -> None:
    detector = GitDetector()

    assert detector.is_repository(str(tmp_path)) is False


def test_branch_without_repository(tmp_path: Path) -> None:
    detector = GitDetector()

    assert detector.branch(str(tmp_path)) is None
