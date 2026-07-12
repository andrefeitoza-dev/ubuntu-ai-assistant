from typer.testing import CliRunner

from ubuntu_ai.cli.app import app

runner = CliRunner()


def test_plan_command() -> None:
    result = runner.invoke(app, ["plan", "Instale Docker"])

    assert result.exit_code == 0
    assert "Instalar e configurar o Docker" in result.stdout
    assert "Atualizar repositórios" in result.stdout
    assert "Nenhum comando foi executado" in result.stdout


def test_plan_command_rejects_unsupported_request() -> None:
    result = runner.invoke(
        app,
        ["plan", "Configure um servidor de e-mail"],
    )

    assert result.exit_code == 1
    assert "Ainda não sei criar um plano" in result.stdout
