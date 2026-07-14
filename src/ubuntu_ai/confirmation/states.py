from enum import StrEnum


class ConfirmationState(StrEnum):
    """Estados possíveis de uma confirmação."""

    WAITING_CONFIRMATION = "waiting_confirmation"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"