import pytest

from ubuntu_ai.benchmark import BenchmarkService


def test_measure_records_success() -> None:
    service = BenchmarkService()
    with service.measure("operation"):
        pass
    record = service.report().records[0]
    assert record.duration >= 0
    assert record.success is True


def test_measure_records_failure_and_reraises() -> None:
    service = BenchmarkService()
    with pytest.raises(RuntimeError, match="falha"):
        with service.measure("operation"):
            raise RuntimeError("falha")
    assert service.report().records[0].success is False
