from ubuntu_ai.domain.plan import Plan, PlanStep, RiskLevel
from ubuntu_ai.executor.preview import PreviewBuilder


def create_plan() -> Plan:
    return Plan(
        goal="Preparar ambiente Docker",
        risk=RiskLevel.HIGH,
        estimated_seconds=120,
        steps=[
            PlanStep(
                title="Verificar Docker",
                description="Verifica se o Docker está instalado.",
                command=["docker", "--version"],
            ),
            PlanStep(
                title="Verificar serviço",
                description="Verifica o estado atual do serviço Docker.",
                command=["systemctl", "status", "docker"],
            ),
        ],
    )


def test_preview_preserves_plan_information() -> None:
    preview = PreviewBuilder().build(create_plan())

    assert preview.goal == "Preparar ambiente Docker"
    assert preview.risk == RiskLevel.HIGH
    assert preview.estimated_seconds == 120
    assert preview.dry_run is True


def test_preview_contains_numbered_steps() -> None:
    preview = PreviewBuilder().build(create_plan())

    assert len(preview.steps) == 2

    assert preview.steps[0].number == 1
    assert preview.steps[0].title == "Verificar Docker"
    assert preview.steps[0].command == ["docker", "--version"]

    assert preview.steps[1].number == 2
    assert preview.steps[1].title == "Verificar serviço"
    assert preview.steps[1].command == ["systemctl", "status", "docker"]


def test_preview_copies_step_commands() -> None:
    plan = create_plan()

    preview = PreviewBuilder().build(plan)
    plan.steps[0].command.append("--verbose")

    assert preview.steps[0].command == ["docker", "--version"]
