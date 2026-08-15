from pathlib import Path

from ubuntu_ai.context.discovery.service import ContextDiscoveryService


def test_discover_environment(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()

    service = ContextDiscoveryService()

    snapshot = service.discover(str(tmp_path))

    assert snapshot.working_directory == str(tmp_path)
    assert snapshot.git_repository is True
    assert snapshot.project_name == tmp_path.name
    assert snapshot.operating_system
    assert snapshot.python_version
