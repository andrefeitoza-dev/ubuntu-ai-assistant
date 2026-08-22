import ast
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_ssh_integration.py"


def test_isolated_ssh_validation_script_is_syntactically_valid() -> None:
    ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))


def test_isolated_ssh_server_binds_only_to_loopback() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert '"127.0.0.1"' in source
    assert '"0.0.0.0"' not in source


def test_isolated_ssh_validation_covers_security_failures() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert "wrong_known_hosts" in source
    assert "wrong_identity" in source
    assert "TimeoutError" in source


def test_isolated_ssh_validation_covers_multi_agent_execution() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert '"uptime"' in source
    assert '"ip route"' in source
    assert '"df -h"' in source
    assert '"systemctl --failed --no-legend --plain"' in source
    assert 'name="isolated-multi-agent"' in source
    assert 'validate_multi_agent, "isolated-multi-agent"' in source
    assert 'os.environ["HOME"] = str(isolated_home)' in source
