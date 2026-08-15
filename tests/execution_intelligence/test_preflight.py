from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.execution_intelligence.preflight import PreflightEngine
from ubuntu_ai.tools.capability import CapabilityCategory, ToolCapability


def capability(*, executable: str, dependency: str | None = None) -> ToolCapability:
    return ToolCapability(
        name="test-tool",
        description="test",
        category=CapabilityCategory.GENERAL,
        executables=(executable,),
        dependencies=(dependency,) if dependency else (),
        risk=RiskLevel.LOW,
    )


def test_preflight_approves_available_executable() -> None:
    report = PreflightEngine().check(capability(executable="python"))
    assert report.ready is True


def test_preflight_blocks_missing_executable() -> None:
    report = PreflightEngine().check(capability(executable="ubuntu-ai-command-that-does-not-exist"))
    assert report.ready is False
    assert report.errors


def test_preflight_blocks_missing_dependency() -> None:
    report = PreflightEngine().check(
        capability(
            executable="python",
            dependency="ubuntu-ai-dependency-that-does-not-exist",
        )
    )
    assert report.ready is False
