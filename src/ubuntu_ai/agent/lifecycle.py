from enum import Enum


class AgentLifecycle(Enum):
    """Estados do ciclo de vida do agente."""

    IDLE = "idle"
    PLANNING = "planning"
    WAITING_CONFIRMATION = "waiting_confirmation"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
