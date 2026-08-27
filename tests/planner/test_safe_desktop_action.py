from pathlib import Path

import pytest

from ubuntu_ai.domain.risk import RiskLevel
from ubuntu_ai.planner.builtin import SafeDesktopActionPlanner


def test_opens_existing_folder_inside_home(tmp_path: Path) -> None:
    downloads = tmp_path / "Downloads"
    downloads.mkdir()
    planner = SafeDesktopActionPlanner(home=tmp_path)

    plan = planner.try_create_plan("abra a pasta Downloads")

    assert plan is not None
    assert plan.risk is RiskLevel.LOW
    assert plan.steps[0].command == ["xdg-open", str(downloads)]


def test_opens_existing_file_inside_home(tmp_path: Path) -> None:
    document = tmp_path / "documento.pdf"
    document.write_text("pdf", encoding="utf-8")
    planner = SafeDesktopActionPlanner(home=tmp_path)

    plan = planner.try_create_plan("abra o arquivo documento.pdf")

    assert plan is not None
    assert plan.steps[0].command == ["xdg-open", str(document)]


@pytest.mark.parametrize(
    ("phrase", "expected"),
    [
        ("acesse o site ubuntu.com", "https://ubuntu.com"),
        ("abra https://www.python.org/docs/", "https://www.python.org/docs/"),
        ("abra o site http://example.com", "http://example.com"),
    ],
)
def test_opens_only_valid_http_sites(phrase: str, expected: str) -> None:
    plan = SafeDesktopActionPlanner().try_create_plan(phrase)

    assert plan is not None
    assert plan.steps[0].command == ["xdg-open", expected]


@pytest.mark.parametrize(
    ("phrase", "app_id"),
    [
        ("abra o Firefox", "firefox"),
        ("abra o terminal", "org.gnome.Terminal"),
        ("inicie a calculadora", "org.gnome.Calculator"),
        ("execute o vscode", "code"),
    ],
)
def test_launches_only_trusted_applications(phrase: str, app_id: str) -> None:
    plan = SafeDesktopActionPlanner().try_create_plan(phrase)

    assert plan is not None
    assert plan.steps[0].command == ["gtk-launch", app_id]


def test_email_request_is_ambiguous_and_not_executed() -> None:
    planner = SafeDesktopActionPlanner()

    assert planner.try_create_plan("abra meu email") is None
    assert "ambíguo" in planner.rejection_reason("abra meu email")


@pytest.mark.parametrize(
    "phrase",
    [
        "abra javascript:alert(1)",
        "abra file:///etc/passwd",
        "abra https://user:password@example.com",
        "abra o aplicativo desconhecido",
    ],
)
def test_rejects_unsafe_urls_and_unknown_apps(phrase: str) -> None:
    planner = SafeDesktopActionPlanner()

    assert planner.try_create_plan(phrase) is None
    assert planner.rejection_reason(phrase) is not None


def test_rejects_path_outside_home(tmp_path: Path) -> None:
    planner = SafeDesktopActionPlanner(home=tmp_path)

    assert planner.try_create_plan("abra o arquivo /etc/passwd") is None
    assert planner.rejection_reason("abra o arquivo /etc/passwd") is not None


@pytest.mark.parametrize(
    ("phrase", "app_id"),
    [
        ("Abra o Firefox.", "firefox"),
        ("Abra as configurações de rede.", "gnome-network-panel"),
        ("Abra o VS Code.", "code"),
    ],
)
def test_catalog_desktop_examples_accept_sentence_period(
    phrase: str,
    app_id: str,
) -> None:
    plan = SafeDesktopActionPlanner().try_create_plan(phrase)

    assert plan is not None
    assert plan.risk is RiskLevel.LOW
    assert plan.steps[0].command == ["gtk-launch", app_id]


def test_catalog_documents_example_accepts_localized_possession(
    tmp_path: Path,
) -> None:
    documents = tmp_path / "Documentos"
    documents.mkdir()
    planner = SafeDesktopActionPlanner(home=tmp_path)

    plan = planner.try_create_plan("Abra minha pasta Documentos.")

    assert plan is not None
    assert plan.risk is RiskLevel.LOW
    assert plan.steps[0].command == ["xdg-open", str(documents)]


def test_documents_alias_uses_xdg_user_directory(
    tmp_path: Path,
) -> None:
    configured_documents = tmp_path / "MeusDocumentos"
    configured_documents.mkdir()

    config = tmp_path / ".config"
    config.mkdir()
    (config / "user-dirs.dirs").write_text(
        'XDG_DOCUMENTS_DIR="$HOME/MeusDocumentos"\n',
        encoding="utf-8",
    )

    planner = SafeDesktopActionPlanner(home=tmp_path)
    plan = planner.try_create_plan("Abra minha pasta Documentos.")

    assert plan is not None
    assert plan.steps[0].command == [
        "xdg-open",
        str(configured_documents),
    ]
