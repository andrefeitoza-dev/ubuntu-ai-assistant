from __future__ import annotations

from pathlib import Path
from unittest.mock import Mock

from ubuntu_ai.gui.interface import apply_busy_state
from ubuntu_ai.gui.theme import ACCENT, SUCCESS, WARNING


def test_busy_state_disables_input_and_enables_cancellation() -> None:
    status = Mock()
    button = Mock()
    entry = Mock()
    submit = Mock()
    cancel = Mock()

    apply_busy_state(
        busy=True,
        label="Processando",
        status_label=status,
        send_button=button,
        request_entry=entry,
        on_submit=submit,
        on_cancel=cancel,
    )

    status.configure.assert_called_once_with(
        text="●  Processando...",
        fg=WARNING,
    )
    button.configure.assert_called_once()
    assert button.configure.call_args.kwargs["command"] is cancel
    entry.configure.assert_called_once_with(state="disabled")
    entry.focus_set.assert_not_called()


def test_ready_state_restores_input_and_submit_action() -> None:
    status = Mock()
    button = Mock()
    entry = Mock()
    submit = Mock()
    cancel = Mock()

    apply_busy_state(
        busy=False,
        label="Ignorado",
        status_label=status,
        send_button=button,
        request_entry=entry,
        on_submit=submit,
        on_cancel=cancel,
    )

    status.configure.assert_called_once_with(
        text="●  Pronto",
        fg=SUCCESS,
    )
    button.configure.assert_called_once()
    assert button.configure.call_args.kwargs["command"] is submit
    assert button.configure.call_args.kwargs["bg"] == ACCENT
    entry.configure.assert_called_once_with(state="normal")
    entry.focus_set.assert_called_once_with()


def test_interface_component_has_no_backend_or_policy_access() -> None:
    source = Path("src/ubuntu_ai/gui/interface.py").read_text(encoding="utf-8")

    assert "_backend" not in source
    assert "ConfirmationEngine" not in source
    assert "ExecutionPolicy" not in source
    assert "messagebox" not in source


def test_conversation_view_has_no_coordination_responsibilities() -> None:
    source = Path("src/ubuntu_ai/gui/conversation_view.py").read_text(encoding="utf-8")

    assert "_backend" not in source
    assert "submit(" not in source
    assert "cancel_current_operation" not in source
    assert "InteractionRoute" not in source
