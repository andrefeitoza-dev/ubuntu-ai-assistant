from ubuntu_ai.core.engine import CoreEngine
from ubuntu_ai.core.intent import Intent


def test_detect_plan() -> None:
    engine = CoreEngine()

    assert engine.detect_intent("Instale Docker") == Intent.PLAN


def test_detect_explain() -> None:
    engine = CoreEngine()

    assert engine.detect_intent("Explique o comando ls") == Intent.EXPLAIN
