from ubuntu_ai.core.intent import Intent


class CoreEngine:
    """Responsável por decidir qual fluxo executar."""

    def detect_intent(self, text: str) -> Intent:
        text = text.lower()

        if "doctor" in text:
            return Intent.DOCTOR

        if "explique" in text:
            return Intent.EXPLAIN

        if "instale" in text or "configure" in text:
            return Intent.PLAN

        return Intent.CHAT
