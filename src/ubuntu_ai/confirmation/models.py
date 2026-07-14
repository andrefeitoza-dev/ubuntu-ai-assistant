from dataclasses import dataclass

from ubuntu_ai.confirmation.states import ConfirmationState


@dataclass(slots=True)
class Confirmation:
    """Representa o estado de confirmação de uma execução."""

    state: ConfirmationState = ConfirmationState.WAITING_CONFIRMATION