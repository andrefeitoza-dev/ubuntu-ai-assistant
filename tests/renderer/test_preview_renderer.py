from ubuntu_ai.domain.plan import RiskLevel
from ubuntu_ai.executor.preview import ExecutionPreview, PreviewStep
from ubuntu_ai.renderer.preview_renderer import PreviewRenderer


def create_preview() -> ExecutionPreview:
    return ExecutionPreview(
        goal="Preparar ambiente Docker",
        risk=RiskLevel.HIGH,
        estimated_seconds=120,
        steps=(
            PreviewStep(
                number=1,
                title="Verificar Docker",
                description="Verifica se o Docker está instalado.",
                command=["docker", "--version"],
            ),
            PreviewStep(
                number=2,
                title="Verificar serviço",
                description="Verifica o estado do serviço Docker.",
                command=["systemctl", "status", "docker"],
            ),
        ),
    )


def test_renderer_displays_preview_header() -> None:
    rendered = PreviewRenderer().render(create_preview())

    assert "Ubuntu AI Assistant" in rendered
    assert "Execution Preview (DRY RUN)" in rendered
    assert "Nenhuma alteração será realizada." in rendered


def test_renderer_displays_plan_information() -> None:
    rendered = PreviewRenderer().render(create_preview())

    assert "Preparar ambiente Docker" in rendered
    assert "HIGH" in rendered
    assert "120 segundos" in rendered


def test_renderer_displays_numbered_steps() -> None:
    rendered = PreviewRenderer().render(create_preview())

    assert "1. Verificar Docker" in rendered
    assert "docker --version" in rendered
    assert "2. Verificar serviço" in rendered
    assert "systemctl status docker" in rendered
