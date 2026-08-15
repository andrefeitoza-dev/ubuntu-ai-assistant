from importlib import import_module
from types import SimpleNamespace

from typer.testing import CliRunner

from ubuntu_ai.cli.app import app

runner = CliRunner()
plan_module = import_module("ubuntu_ai.cli.plan")


class FakePipeline:
    def __init__(
        self,
        rendered_preview: str = "",
        error: ValueError | None = None,
    ) -> None:
        self._rendered_preview = rendered_preview
        self._error = error

    def run(self, request: str) -> SimpleNamespace:
        if self._error is not None:
            raise self._error

        return SimpleNamespace(
            rendered_preview=self._rendered_preview,
        )


def test_plan_command_displays_execution_preview(monkeypatch) -> None:
    pipeline = FakePipeline(
        rendered_preview=(
            "Execution Preview (DRY RUN)\n"
            "Instalar e configurar o Docker\n"
            "Atualizar repositórios\n"
            "Nenhuma alteração será realizada.\n"
            "Modo de simulação ativo."
        )
    )

    monkeypatch.setattr(
        plan_module.container,
        "execution_pipeline",
        lambda: pipeline,
    )

    result = runner.invoke(app, ["plan", "Instale Docker"])

    assert result.exit_code == 0
    assert "Execution Preview (DRY RUN)" in result.stdout
    assert "Instalar e configurar o Docker" in result.stdout
    assert "Atualizar repositórios" in result.stdout
    assert "Nenhuma alteração será realizada." in result.stdout


def test_plan_command_displays_pipeline_error(monkeypatch) -> None:
    pipeline = FakePipeline(
        error=ValueError("Falha ao criar o plano."),
    )

    monkeypatch.setattr(
        plan_module.container,
        "execution_pipeline",
        lambda: pipeline,
    )

    result = runner.invoke(
        app,
        ["plan", "Configure um servidor de e-mail"],
    )

    assert result.exit_code == 1
    assert "Falha ao criar o plano" in result.stdout


def test_plan_command_rejects_empty_request(monkeypatch) -> None:
    pipeline = FakePipeline(
        error=ValueError("A solicitação não pode estar vazia."),
    )

    monkeypatch.setattr(
        plan_module.container,
        "execution_pipeline",
        lambda: pipeline,
    )

    result = runner.invoke(app, ["plan", "   "])

    assert result.exit_code == 1
    assert "solicitação não pode estar vazia" in result.stdout
