import pytest

from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.tools.capability import CapabilityCategory, ToolCapability
from ubuntu_ai.tools.capability_registry import CapabilityRegistry


def capability(name: str = "apt") -> ToolCapability:
    return ToolCapability(
        name=name,
        description="Teste",
        category=CapabilityCategory.PACKAGE,
        executables=(name,),
        risk=RiskLevel.HIGH,
    )


def test_register_and_find_capability_by_executable() -> None:
    registry = CapabilityRegistry((capability(),))

    assert registry.get("APT").name == "apt"
    assert registry.for_executable("apt")[0].name == "apt"


def test_rejects_duplicate_capability() -> None:
    registry = CapabilityRegistry((capability(),))

    with pytest.raises(ValueError, match="Capacidade já registrada"):
        registry.register(capability())


def test_replace_capability_explicitly() -> None:
    registry = CapabilityRegistry((capability(),))
    replacement = capability("apt")

    registry.register(replacement, replace=True)

    assert registry.get("apt") is replacement
