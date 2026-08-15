import pytest

from ubuntu_ai.benchmark import BenchmarkRecord


def test_record_rejects_empty_operation() -> None:
    with pytest.raises(ValueError, match="não pode estar vazia"):
        BenchmarkRecord(operation="", duration=0.1)


def test_record_rejects_negative_duration() -> None:
    with pytest.raises(ValueError, match="não pode ser negativa"):
        BenchmarkRecord(operation="planner", duration=-0.1)
