from pathlib import Path

import pytest

from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.planner.builtin import SafeFileSearchPlanner


@pytest.mark.parametrize(
    ("phrase", "item_type", "term"),
    [
        ("encontre o arquivo relatório.pdf", "f", "relatório.pdf"),
        ("procure a pasta Projetos", "d", "Projetos"),
        ("onde está README.md?", None, "README.md"),
        ("localize ubuntu-ai no computador", None, "ubuntu-ai"),
    ],
)
def test_builds_structured_read_only_search(
    phrase: str,
    item_type: str | None,
    term: str,
) -> None:
    planner = SafeFileSearchPlanner(home=Path("/home/teste"))

    plan = planner.try_create_plan(phrase)

    assert plan is not None
    assert plan.risk is RiskLevel.LOW
    command = plan.steps[0].command
    assert command[:4] == ["find", "/home/teste", "-maxdepth", "6"]
    assert command[-3:] == ["-iname", f"*{term}*", "-print"]
    if item_type is not None:
        assert ["-type", item_type] == command[4:6]


@pytest.mark.parametrize(
    "phrase",
    [
        "encontre o arquivo ../../etc/passwd",
        "procure a pasta teste; rm -rf /",
        "localize arquivo | cat /etc/shadow",
        "onde está ..",
        "encontre o arquivo",
    ],
)
def test_rejects_ambiguous_or_shell_like_search(phrase: str) -> None:
    planner = SafeFileSearchPlanner(home=Path("/home/teste"))

    assert planner.try_create_plan(phrase) is None


def test_glob_characters_are_treated_as_literal_text() -> None:
    planner = SafeFileSearchPlanner(home=Path("/home/teste"))

    plan = planner.try_create_plan("encontre o arquivo *.env")

    assert plan is not None
    assert plan.steps[0].command[-2] == "*[*].env*"
