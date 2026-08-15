from io import StringIO

from rich.console import Console

from ubuntu_ai.domain.plan import Plan, PlanStep
from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.tui.plan_renderer import PlanRenderer


def test_plan_renderer_displays_plan_summary_and_steps() -> None:
    output = StringIO()
    console = Console(
        file=output,
        force_terminal=False,
        width=120,
    )
    plan = Plan(
        goal="Instalar Docker",
        estimated_seconds=120,
        risk=RiskLevel.LOW,
    )
    plan.add_step(
        PlanStep(
            title="Instalar",
            description="Instala Docker",
            command=["apt", "install", "docker.io"],
            tool_name="shell",
        )
    )

    PlanRenderer(console).render(plan)

    rendered = output.getvalue()
    assert "Instalar Docker" in rendered
    assert "Etapas do plano" in rendered
    assert "Instalar" in rendered
