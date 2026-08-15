from ubuntu_ai.autonomy.progress import ProgressTracker


def test_progress_ratio() -> None:
    progress = ProgressTracker().calculate(
        completed_steps=2,
        total_steps=4,
    )

    assert progress.ratio == 0.5
