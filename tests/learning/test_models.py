from ubuntu_ai.learning.models import LearningOutcome, LearningPattern


def test_pattern_tracks_outcomes_and_confidence() -> None:
    pattern = LearningPattern.create(request_pattern="listar arquivos", command="ls")
    pattern = pattern.with_outcome(LearningOutcome.SUCCESS)
    pattern = pattern.with_outcome(LearningOutcome.FAILURE)

    assert pattern.attempts == 2
    assert pattern.success_count == 1
    assert pattern.failure_count == 1
    assert pattern.confidence == 0.5
