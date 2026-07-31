from ubuntu_ai.domain.plan import Plan
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.reflection import ReflectionEngine, ReflectionPhase


def test_engine_exposes_pre_execution_reflection() -> None:
    report = ReflectionEngine().before_execution(Plan("Nada", 0, RiskLevel.LOW))

    assert report.phase is ReflectionPhase.PLAN
    assert report.approved is False
