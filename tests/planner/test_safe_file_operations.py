from pathlib import Path

import pytest

from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.planner.builtin import SafeFileOperationPlanner


def test_create_folder_requires_preview_and_nonexistent_destination(tmp_path: Path) -> None:
    planner = SafeFileOperationPlanner(home=tmp_path)

    plan = planner.try_create_plan("Crie a pasta Projetos.")

    assert plan is not None
    assert plan.risk is RiskLevel.HIGH
    assert plan.steps[0].command == ["mkdir", str(tmp_path / "Projetos")]
    assert plan.steps[1].command == ["xdg-open", str(tmp_path)]


def test_create_file_uses_fast_safe_plan(tmp_path: Path) -> None:
    plan = SafeFileOperationPlanner(home=tmp_path).try_create_plan("Crie um arquivo teste011.")

    assert plan is not None
    assert plan.risk is RiskLevel.HIGH
    assert plan.steps[0].command == ["touch", str(tmp_path / "teste011")]
    assert plan.steps[1].command == ["xdg-open", str(tmp_path)]


def test_create_file_inside_existing_home_folder(tmp_path: Path) -> None:
    folder = tmp_path / "Andre07"
    folder.mkdir()

    plan = SafeFileOperationPlanner(home=tmp_path).try_create_plan(
        "Crie um arquivo t01 dentro da pasta Andre07."
    )

    assert plan is not None
    assert plan.steps[0].command == ["touch", str(folder / "t01")]
    assert plan.steps[1].command == ["xdg-open", str(folder)]


def test_create_file_rejects_missing_or_unsafe_custom_folder(tmp_path: Path) -> None:
    planner = SafeFileOperationPlanner(home=tmp_path)

    assert planner.try_create_plan("Crie um arquivo t01 dentro da pasta inexistente.") is None
    assert planner.try_create_plan("Crie um arquivo t01 dentro de ../../etc.") is None


@pytest.mark.parametrize(
    "phrase",
    (
        "Remova a pasta test02 da Home.",
        "Apague a pasta test02.",
        "Delete a pasta test02 da home.",
    ),
)
def test_remove_folder_uses_recoverable_trash(tmp_path: Path, phrase: str) -> None:
    source = tmp_path / "test02"
    source.mkdir()

    plan = SafeFileOperationPlanner(home=tmp_path).try_create_plan(phrase)

    assert plan is not None
    assert plan.risk is RiskLevel.HIGH
    assert plan.steps[0].command == ["gio", "trash", str(source)]


@pytest.mark.parametrize("verb", ("Copie", "Mova"))
def test_transfer_file_between_known_personal_folders(tmp_path: Path, verb: str) -> None:
    documents = tmp_path / "Documentos"
    downloads = tmp_path / "Downloads"
    documents.mkdir()
    downloads.mkdir()
    source = documents / "relatório.pdf"
    source.write_text("conteúdo", encoding="utf-8")

    plan = SafeFileOperationPlanner(home=tmp_path).try_create_plan(
        f"{verb} o arquivo relatório.pdf de Documentos para Downloads."
    )

    assert plan is not None
    assert plan.risk is RiskLevel.HIGH
    assert plan.steps[0].command[0] == ("cp" if verb == "Copie" else "mv")
    assert plan.steps[0].command[1:] == [str(source), str(downloads / source.name)]


def test_rename_does_not_overwrite_existing_item(tmp_path: Path) -> None:
    (tmp_path / "antigo.txt").write_text("a", encoding="utf-8")
    (tmp_path / "novo.txt").write_text("b", encoding="utf-8")
    planner = SafeFileOperationPlanner(home=tmp_path)

    assert planner.try_create_plan("Renomeie o arquivo antigo.txt para novo.txt.") is None
    assert "destino não pode existir" in planner.rejection_reason(
        "Renomeie o arquivo antigo.txt para novo.txt."
    )


def test_moves_item_to_recoverable_trash_with_high_risk(tmp_path: Path) -> None:
    source = tmp_path / "rascunho.txt"
    source.write_text("dados", encoding="utf-8")

    plan = SafeFileOperationPlanner(home=tmp_path).try_create_plan(
        "Envie o arquivo rascunho.txt para a Lixeira."
    )

    assert plan is not None
    assert plan.risk is RiskLevel.HIGH
    assert plan.steps[0].command == ["gio", "trash", str(source)]


@pytest.mark.parametrize(
    "phrase",
    (
        "Crie a pasta ../../fora.",
        "Crie a pasta teste; rm -rf /.",
        "Copie o arquivo segredo de /etc para Downloads.",
        "Renomeie o arquivo link para destino.",
    ),
)
def test_rejects_unsafe_or_unverifiable_changes(tmp_path: Path, phrase: str) -> None:
    assert SafeFileOperationPlanner(home=tmp_path).try_create_plan(phrase) is None
