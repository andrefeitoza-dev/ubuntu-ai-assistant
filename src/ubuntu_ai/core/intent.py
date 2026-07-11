from enum import StrEnum


class Intent(StrEnum):
    DOCTOR = "doctor"
    CHAT = "chat"
    PLAN = "plan"
    EXECUTE = "execute"
    EXPLAIN = "explain"
    UNKNOWN = "unknown"
