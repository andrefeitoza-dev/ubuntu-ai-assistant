from pathlib import Path

import pytest

from ubuntu_ai.planner.builtin import CapabilityActionPlanner


@pytest.mark.parametrize(
    ("phrase", "expected_command"),
    (
        (
            "Localize arquivos PDF em Documentos.",
            ("find", "-type", "f", "-iname", "*.pdf"),
        ),
        (
            "Qual pasta ocupa mais espaço?",
            ("du", "--max-depth=1"),
        ),
        (
            "Quais processos usam mais memória?",
            ("ps", "--sort=-%mem"),
        ),
        (
            "Mostre os logs do serviço Docker.",
            ("journalctl", "docker.service", "-n", "100"),
        ),
    ),
)
def test_advertised_queries_receive_deterministic_read_only_plans(
    tmp_path: Path,
    phrase: str,
    expected_command: tuple[str, ...],
) -> None:
    documents = tmp_path / "Documents"
    documents.mkdir()

    plan = CapabilityActionPlanner(home=tmp_path).try_create_plan(phrase)

    assert plan is not None
    assert plan.risk.value == "low"
    command = plan.steps[0].command

    for item in expected_command:
        assert item in command


def test_pdf_search_is_restricted_to_documents(tmp_path: Path) -> None:
    documents = tmp_path / "Documents"
    documents.mkdir()

    plan = CapabilityActionPlanner(home=tmp_path).try_create_plan(
        "Localize arquivos PDF em Documentos."
    )

    assert plan is not None
    command = plan.steps[0].command
    assert str(documents) in command
    assert "*.pdf" in command
    assert "*arquivos PDF em Documentos*" not in command


@pytest.mark.parametrize(
    ("phrase", "executable"),
    (
        ("Encontre PDFs na pasta Documentos.", "find"),
        ("Procure arquivos PDF em Documents.", "find"),
        ("Mostre qual diretório usa mais espaço.", "du"),
        ("Qual é a maior pasta por uso de espaço?", "du"),
        ("Liste os processos com maior uso de memória.", "ps"),
        ("Mostre o consumo de memória dos processos.", "ps"),
        ("Mostre os logs do Docker.", "journalctl"),
        ("Exiba os registros do serviço Docker.", "journalctl"),
        ("Quero ver o journal do Docker.", "journalctl"),
    ),
)
def test_natural_variations_keep_the_safe_deterministic_route(
    tmp_path: Path,
    phrase: str,
    executable: str,
) -> None:
    (tmp_path / "Documents").mkdir()

    plan = CapabilityActionPlanner(home=tmp_path).try_create_plan(phrase)

    assert plan is not None
    assert plan.risk.value == "low"
    assert plan.steps[0].command[0] == executable
