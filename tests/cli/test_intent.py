from typer.testing import CliRunner

from ubuntu_ai.cli.app import app

runner = CliRunner()


def test_intent_command_displays_structured_interpretation() -> None:
    result = runner.invoke(app, ["intent", "Instale Docker"])

    assert result.exit_code == 0
    assert "Ubuntu AI — Intent" in result.stdout
    assert "installation" in result.stdout
    assert "provision" in result.stdout
    assert "docker" in result.stdout
