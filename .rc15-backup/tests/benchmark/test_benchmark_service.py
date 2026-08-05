from ubuntu_ai.benchmark import BenchmarkService


def test_records_are_accumulated() -> None:
    service = BenchmarkService()

    service.record("planner", 0.25)
    service.record("pipeline", 0.50)

    report = service.report()

    assert report.operations == 2
    assert report.total_duration == 0.75
    assert report.average_duration == 0.375


def test_clear_removes_records() -> None:
    service = BenchmarkService()

    service.record("planner", 0.25)
    service.clear()

    report = service.report()

    assert report.operations == 0
    assert report.total_duration == 0.0