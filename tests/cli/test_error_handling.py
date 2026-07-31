from importlib import import_module

from typer.testing import CliRunner

from ubuntu_ai.cli.app import app

runner = CliRunner()
plan_module = import_module("ubuntu_ai.cli.plan")


class BrokenPipeline:
    def run(self, request: str) -> object:
        raise RuntimeError("Falha ao gerar resposta com o Ollama.")


def test_plan_hides_traceback_by_default(monkeypatch) -> None:
    monkeypatch.setattr(
        plan_module.container,
        "execution_pipeline",
        lambda: BrokenPipeline(),
    )

    result = runner.invoke(app, ["plan", "mostrar diretório"])

    assert result.exit_code == 1
    assert "Erro ao gerar o plano" in result.stdout
    assert "diagnose-ai" in result.stdout
    assert "Traceback" not in result.stdout


def test_plan_debug_mode_preserves_original_exception(monkeypatch) -> None:
    monkeypatch.setattr(
        plan_module.container,
        "execution_pipeline",
        lambda: BrokenPipeline(),
    )

    result = runner.invoke(
        app,
        ["--debug", "plan", "mostrar diretório"],
        catch_exceptions=True,
    )

    assert result.exit_code == 1
    assert isinstance(result.exception, RuntimeError)
