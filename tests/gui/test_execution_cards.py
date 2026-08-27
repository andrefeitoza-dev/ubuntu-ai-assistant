from __future__ import annotations

from enum import Enum
from pathlib import Path
from types import SimpleNamespace

from ubuntu_ai.gui.execution_cards import (
    execution_output,
    execution_status_value,
    execution_succeeded,
)


class ResultStatus(Enum):
    EXECUTED = "executed"
    FAILED = "failed"


def test_execution_status_accepts_enum_and_text() -> None:
    enum_result = SimpleNamespace(status=ResultStatus.EXECUTED)
    text_result = SimpleNamespace(status="FAILED")

    assert execution_status_value(enum_result) == "executed"
    assert execution_status_value(text_result) == "failed"


def test_execution_success_recognizes_supported_statuses() -> None:
    for status in ("approved", "executed", "success", "succeeded"):
        assert execution_succeeded(SimpleNamespace(status=status))

    assert not execution_succeeded(SimpleNamespace(status="failed"))


def test_execution_output_prefers_stdout_and_falls_back_to_stderr() -> None:
    assert execution_output(SimpleNamespace(stdout="resultado", stderr="erro")) == "resultado"
    assert execution_output(SimpleNamespace(stdout="", stderr="falha")) == "falha"


def test_visual_component_does_not_access_backend_or_policy() -> None:
    source = Path("src/ubuntu_ai/gui/execution_cards.py").read_text(encoding="utf-8")

    assert "_backend" not in source
    assert "ConfirmationEngine" not in source
    assert "ExecutionPolicy" not in source
    assert "messagebox" not in source
