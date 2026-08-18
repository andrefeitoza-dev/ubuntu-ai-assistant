from ubuntu_ai.learning.models import LearningOutcome, LearningPattern


def test_pattern_tracks_outcomes_and_confidence() -> None:
    pattern = LearningPattern.create(request_pattern="listar arquivos", command="ls")
    pattern = pattern.with_outcome(LearningOutcome.SUCCESS)
    pattern = pattern.with_outcome(LearningOutcome.FAILURE)

    assert pattern.attempts == 2
    assert pattern.success_count == 1
    assert pattern.failure_count == 1
    assert pattern.confidence == 0.5


def test_pattern_requires_success_and_positive_feedback_for_reuse() -> None:
    pattern = LearningPattern.create(request_pattern="listar arquivos", command="ls")
    pattern = pattern.with_outcome(LearningOutcome.SUCCESS)

    assert pattern.approved_for_reuse is False
    assert pattern.with_feedback(helpful=True).approved_for_reuse is True


def test_failed_pattern_cannot_be_approved_for_reuse() -> None:
    pattern = LearningPattern.create(request_pattern="listar arquivos", command="ls")
    pattern = pattern.with_outcome(LearningOutcome.SUCCESS)
    pattern = pattern.with_outcome(LearningOutcome.FAILURE)
    pattern = pattern.with_feedback(helpful=True)

    assert pattern.approved_for_reuse is False
