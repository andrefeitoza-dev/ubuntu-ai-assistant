from ubuntu_ai.confirmation.engine import ConfirmationEngine
from ubuntu_ai.confirmation.states import ConfirmationState


def test_new_confirmation_starts_waiting() -> None:
    engine = ConfirmationEngine()

    confirmation = engine.create()

    assert confirmation.state == ConfirmationState.WAITING_CONFIRMATION


def test_confirmation_can_be_confirmed() -> None:
    engine = ConfirmationEngine()

    confirmation = engine.create()

    engine.confirm(confirmation)

    assert confirmation.state == ConfirmationState.CONFIRMED


def test_confirmation_can_be_cancelled() -> None:
    engine = ConfirmationEngine()

    confirmation = engine.create()

    engine.cancel(confirmation)

    assert confirmation.state == ConfirmationState.CANCELLED