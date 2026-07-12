from typer.testing import CliRunner

from ubuntu_ai.cli.app import app

runner = CliRunner()


def test_plan_command_displays_execution_preview() -> None:
    result = runner.invoke(app, ["plan", "Instale Docker"])

    assert result.exit_code == 0
    assert "Execution Preview (DRY RUN)" in result.stdout
    assert "Instalar e configurar o Docker" in result.stdout
    assert "Atualizar repositórios" in result.stdout
    assert "Nenhuma alteração será realizada." in result.stdout
    assert "Modo de simulação ativo." in result.stdout


def test_plan_command_rejects_unsupported_request() -> None:
    result = runner.invoke(
        app,
        ["plan", "Configure um servidor de e-mail"],
    )

    assert result.exit_code == 1
    assert "Ainda não sei criar um plano" in result.stdout


def test_plan_command_rejects_empty_request() -> None:
    result = runner.invoke(app, ["plan", "   "])

    assert result.exit_code == 1
    assert "solicitação não pode estar vazia" in result.stdout