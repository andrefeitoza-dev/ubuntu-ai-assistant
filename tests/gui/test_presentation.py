from __future__ import annotations

from types import SimpleNamespace

import pytest

from ubuntu_ai.agent_loop.models import LoopState
from ubuntu_ai.gui.presentation import (
    command_text,
    format_duration,
    friendly_error,
    risk_color,
    risk_label,
    state_message,
)


@pytest.mark.parametrize(
    ("message", "expected"),
    (
        ("", "backend não informou"),
        ("Ollama connection refused", "conectar ao Ollama"),
        ("request timed out", "tempo esperado"),
        ("model not found", "modelo de IA"),
        ("permissão negada", "negou permissão"),
        ("erro desconhecido", "erro desconhecido"),
    ),
)
def test_friendly_error_covers_known_failures(
    message: str,
    expected: str,
) -> None:
    assert expected in friendly_error(message)


@pytest.mark.parametrize(
    ("duration", "expected"),
    (
        (0.0004, "400 µs"),
        (0.125, "125.0 ms"),
        (2.5, "2.50 s"),
    ),
)
def test_format_duration_adapts_to_latency_scale(
    duration: float,
    expected: str,
) -> None:
    assert format_duration(duration) == expected


def test_command_text_formats_sequences_and_scalar_values() -> None:
    assert command_text(("git", "status")) == "git status"
    assert command_text(["python", "-V"]) == "python -V"
    assert command_text("uptime") == "uptime"


@pytest.mark.parametrize(
    ("state", "expected"),
    (
        (LoopState.COMPLETED, "concluída com sucesso"),
        (LoopState.BLOCKED, "bloqueada"),
        (LoopState.FAILED, "Não foi possível"),
        (LoopState.CANCELLED, "cancelada"),
        (LoopState.WAITING_CONFIRMATION, "aguarda"),
    ),
)
def test_state_message_covers_public_loop_states(
    state: LoopState,
    expected: str,
) -> None:
    snapshot = SimpleNamespace(state=state)

    assert expected in state_message(snapshot)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("risk", "expected"),
    (
        ("low", "Risco baixo"),
        ("MEDIUM", "Risco médio"),
        ("high", "Risco alto"),
        ("critical", "Risco crítico"),
        ("custom", "Risco custom"),
    ),
)
def test_risk_label_translates_known_levels(
    risk: str,
    expected: str,
) -> None:
    assert risk_label(risk) == expected


@pytest.mark.parametrize(
    ("risk", "expected"),
    (
        ("low", "green"),
        ("MEDIUM", "yellow"),
        ("high", "red"),
        ("critical", "red"),
    ),
)
def test_risk_color_uses_injected_theme(
    risk: str,
    expected: str,
) -> None:
    assert (
        risk_color(
            risk,
            success="green",
            warning="yellow",
            error="red",
        )
        == expected
    )
