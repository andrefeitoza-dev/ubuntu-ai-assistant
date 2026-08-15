from pathlib import Path

from ubuntu_ai.learning.models import LearningOutcome, LearningPattern
from ubuntu_ai.learning.sqlite_repository import SQLiteLearningRepository


def test_repository_aggregates_repeated_outcomes(tmp_path: Path) -> None:
    repository = SQLiteLearningRepository(tmp_path / "learning.db")
    first = LearningPattern.create(request_pattern="listar arquivos", command="ls")

    saved = repository.record_outcome(first, LearningOutcome.SUCCESS)
    saved = repository.record_outcome(first, LearningOutcome.FAILURE)

    assert saved.success_count == 1
    assert saved.failure_count == 1
    assert len(repository.list_patterns()) == 1
    assert repository.get_pattern(saved.id) == saved


def test_repository_records_feedback(tmp_path: Path) -> None:
    repository = SQLiteLearningRepository(tmp_path / "learning.db")
    saved = repository.record_outcome(
        LearningPattern.create(request_pattern="ver disco", command="df -h"),
        LearningOutcome.SUCCESS,
    )

    updated = repository.record_feedback(saved.id, helpful=True)

    assert updated.positive_feedback == 1
