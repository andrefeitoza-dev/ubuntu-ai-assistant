from ubuntu_ai.confirmation.states import ConfirmationState


def test_confirmation_states() -> None:
    assert ConfirmationState.WAITING_CONFIRMATION.value == "waiting_confirmation"
    assert ConfirmationState.CONFIRMED.value == "confirmed"
    assert ConfirmationState.CANCELLED.value == "cancelled"
