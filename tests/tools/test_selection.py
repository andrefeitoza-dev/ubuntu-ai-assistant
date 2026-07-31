from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.tools.capability_registry import CapabilityRegistry
from ubuntu_ai.tools.default_capabilities import default_capabilities
from ubuntu_ai.tools.selection import ToolSelectionEngine


def selector() -> ToolSelectionEngine:
    return ToolSelectionEngine(CapabilityRegistry(default_capabilities()))


def test_selects_apt_behind_sudo_wrapper() -> None:
    step = PlanStep(
        title="Instalar pacote",
        description="Instala o Docker no Ubuntu.",
        command=["sudo", "apt", "install", "docker.io"],
    )

    result = selector().select(step, request="Instale Docker")

    assert result.capability.name == "apt"
    assert "executável compatível: apt" in result.reasons


def test_selects_systemctl_for_service_command() -> None:
    step = PlanStep(
        title="Habilitar serviço",
        description="Habilita o Docker.",
        command=["sudo", "systemctl", "enable", "docker"],
    )

    result = selector().select(step, request="Configure Docker")

    assert result.capability.name == "systemctl"


def test_uses_shell_as_fallback_for_unknown_executable() -> None:
    step = PlanStep(
        title="Executar utilitário",
        description="Executa uma ferramenta específica.",
        command=["custom-command", "--check"],
    )

    result = selector().select(step, request="Faça uma verificação")

    assert result.capability.name == "shell"


def test_select_plan_preserves_plan_and_adds_tool_names() -> None:
    plan = Plan(
        goal="Instalar e verificar Docker",
        estimated_seconds=30,
        risk=RiskLevel.HIGH,
        steps=[
            PlanStep("Instalar", "Instala Docker", ["sudo", "apt", "install", "docker.io"]),
            PlanStep("Verificar", "Verifica Docker", ["docker", "--version"]),
        ],
    )

    selected = selector().select_plan(plan, request="Instale Docker")

    assert selected is not plan
    assert [step.tool_name for step in selected.steps] == ["apt", "docker"]
    assert [step.tool_name for step in plan.steps] == [None, None]
