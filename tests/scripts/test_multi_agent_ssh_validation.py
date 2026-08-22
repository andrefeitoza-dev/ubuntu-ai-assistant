import ast
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "validate_multi_agent_ssh.py"


def test_multi_agent_ssh_validator_is_syntactically_valid() -> None:
    ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))


def test_multi_agent_ssh_validator_requires_remote_target_and_audit() -> None:
    source = SCRIPT.read_text(encoding="utf-8")

    assert 'host.name.lower() == "local"' in source
    assert 'goal.context["environment"] != "remote"' in source
    assert "backend.register_multi_agent(goal)" in source
    assert "backend.execute_multi_agent(goal, confirmed=True)" in source
    assert "backend.remote_audit_records()" in source
    assert 'record.status == "completed"' in source
