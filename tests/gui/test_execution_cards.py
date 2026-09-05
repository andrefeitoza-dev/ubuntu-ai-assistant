from __future__ import annotations

from enum import Enum
from pathlib import Path
from types import SimpleNamespace

from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.gui.execution_cards import (
    execution_output,
    execution_status_value,
    execution_succeeded,
    file_execution_confirmation,
    plan_risk_tone,
)
from ubuntu_ai.gui.theme import ERROR, SUCCESS, WARNING


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


def test_created_file_confirmation_exposes_real_path_and_refresh_hint() -> None:
    result = SimpleNamespace(
        status="executed",
        command="touch /home/user/Andre07/t01",
    )

    confirmation = file_execution_confirmation(result)

    assert confirmation is not None
    assert "/home/user/Andre07/t01" in confirmation
    assert "F5" in confirmation


def test_file_confirmation_requires_successful_real_creation() -> None:
    failed = SimpleNamespace(status="failed", command="touch /home/user/t01")
    unrelated = SimpleNamespace(status="executed", command="ls -la")

    assert file_execution_confirmation(failed) is None
    assert file_execution_confirmation(unrelated) is None


def test_visual_component_does_not_access_backend_or_policy() -> None:
    source = Path("src/ubuntu_ai/gui/execution_cards.py").read_text(encoding="utf-8")

    assert "_backend" not in source
    assert "ConfirmationEngine" not in source
    assert "ExecutionPolicy" not in source
    assert "messagebox" not in source


def test_plan_card_maps_real_risk_enum_to_theme_color() -> None:
    assert plan_risk_tone(RiskLevel.LOW) == SUCCESS
    assert plan_risk_tone(RiskLevel.MEDIUM) == WARNING
    assert plan_risk_tone(RiskLevel.HIGH) == ERROR


def test_plan_step_exposes_structured_command() -> None:
    step = SimpleNamespace(command=["mkdir", "/home/user/Teste"])

    assert step.command == ["mkdir", "/home/user/Teste"]
