from ubuntu_ai.confirmation.models import Confirmation
from ubuntu_ai.confirmation.states import ConfirmationState


class ConfirmationEngine:
    """Gerencia o estado de confirmação de uma execução."""

    def create(self) -> Confirmation:
        """Cria uma confirmação aguardando decisão."""

        return Confirmation()

    def confirm(self, confirmation: Confirmation) -> None:
        """Marca a confirmação como aprovada."""

        confirmation.state = ConfirmationState.CONFIRMED

    def cancel(self, confirmation: Confirmation) -> None:
        """Marca a confirmação como cancelada."""

        confirmation.state = ConfirmationState.CANCELLED
