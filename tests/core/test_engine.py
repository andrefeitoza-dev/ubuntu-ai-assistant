from ubuntu_ai.core.engine import CoreEngine
from ubuntu_ai.core.intent import Intent


def test_detect_intent_plan() -> None:
    engine = CoreEngine()

    intent = engine.detect_intent("Instale Docker e PostgreSQL")

    assert intent == Intent.PLAN


def test_detect_intent_chat() -> None:
    engine = CoreEngine()

    intent = engine.detect_intent("Olá, tudo bem?")

    assert intent == Intent.CHAT


def test_process_plan() -> None:
    engine = CoreEngine()

    response = engine.process("Instale Docker")

    assert "Objetivo:" in response
    assert "Etapas:" in response
    assert "Docker" in response


def test_process_chat() -> None:
    engine = CoreEngine()

    response = engine.process("Bom dia")

    assert response == "Modo Chat"