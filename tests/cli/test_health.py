from typer.testing import CliRunner

from ubuntu_ai.cli.app import app

runner = CliRunner()


def test_health_command_is_registered() -> None:
    result = runner.invoke(app, ["health"])

    assert result.exit_code == 0
    assert "Saúde da aplicação" in result.stdout
